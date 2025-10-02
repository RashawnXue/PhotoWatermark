import json
import os
import re
import hashlib
import base64
from datetime import datetime
from typing import List, Dict, Optional

from .config import WatermarkConfig


def _get_default_config_dir() -> str:
    """Return a reasonable per-user config directory depending on platform."""
    try:
        import sys
        if sys.platform == 'darwin':
            base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
        elif sys.platform.startswith('win'):
            base = os.environ.get('APPDATA', os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming'))
        else:
            base = os.path.join(os.path.expanduser('~'), '.local', 'share')
    except Exception:
        base = os.path.join(os.path.expanduser('~'), '.photowatermark')

    return os.path.join(base, 'PhotoWatermark')


class TemplateManager:
    """Manage saving/loading of watermark templates and last session state.

    Templates are stored as individual JSON files under <config_dir>/templates/.
    A last_session.json file is used to persist the most recent session config for auto-restore.
    """

    TEMPLATE_VERSION = "2.3"

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or _get_default_config_dir()
        self.templates_dir = os.path.join(self.config_dir, 'templates')
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        os.makedirs(self.templates_dir, exist_ok=True)

    def _sanitize_name(self, name: str) -> str:
        """Generate a safe filename from template name.
        
        Uses a combination of cleaned name and hash to ensure uniqueness
        while maintaining some readability.
        """
        name = name.strip()
        if not name:
            return 'unnamed'
        
        # Create a readable part by keeping safe characters
        safe_part = re.sub(r'[^A-Za-z0-9_\-]', '', name)
        if not safe_part:
            safe_part = 'template'
        
        # Limit length of readable part
        if len(safe_part) > 20:
            safe_part = safe_part[:20]
        
        # Create a hash of the original name to ensure uniqueness
        name_hash = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
        
        return f"{safe_part}_{name_hash}"

    def _template_filepath(self, name: str) -> str:
        safe = self._sanitize_name(name)
        return os.path.join(self.templates_dir, f"{safe}.json")

    def save_template(self, name: str, config: WatermarkConfig, description: str = "") -> None:
        """Save a template atomically.

        Raises exceptions on IO errors.
        """
        now = datetime.utcnow().isoformat() + 'Z'
        path = self._template_filepath(name)

        meta = {
            'template_version': self.TEMPLATE_VERSION,
            'name': name,
            'description': description,
            'created_at': now,
            'modified_at': now,
        }

        data = config.to_dict()
        data['_meta'] = meta

        # atomic write
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, path)

    def list_templates(self) -> List[Dict]:
        """Return a list of templates metadata available."""
        items = []
        for fname in sorted(os.listdir(self.templates_dir)):
            if not fname.lower().endswith('.json'):
                continue
            full = os.path.join(self.templates_dir, fname)
            try:
                with open(full, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                meta = data.get('_meta', {})
                items.append({
                    'name': meta.get('name', os.path.splitext(fname)[0]),
                    'path': full,
                    'created_at': meta.get('created_at'),
                    'modified_at': meta.get('modified_at'),
                    'description': meta.get('description', '')
                })
            except Exception:
                # ignore malformed template files
                continue
        return items

    def load_template(self, name: str) -> WatermarkConfig:
        path = self._template_filepath(name)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # remove meta before building
        data.pop('_meta', None)
        return WatermarkConfig.from_dict(data)

    def delete_template(self, name: str) -> None:
        path = self._template_filepath(name)
        if os.path.exists(path):
            os.remove(path)

    def rename_template(self, old_name: str, new_name: str) -> None:
        """Rename a template and update its metadata."""
        old_path = self._template_filepath(old_name)
        new_path = self._template_filepath(new_name)
        if not os.path.exists(old_path):
            raise FileNotFoundError(old_path)
        
        # Check if new name already exists
        if os.path.exists(new_path):
            raise FileExistsError(f"Template '{new_name}' already exists")
        
        # Load the template data
        with open(old_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update metadata
        meta = data.get('_meta', {})
        meta['name'] = new_name
        meta['modified_at'] = datetime.utcnow().isoformat() + 'Z'
        data['_meta'] = meta
        
        # Save to new location atomically
        tmp_path = new_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        
        # Atomic operations: first create new file, then remove old
        os.replace(tmp_path, new_path)
        os.remove(old_path)

    # last session handling
    def _last_session_path(self) -> str:
        return os.path.join(self.config_dir, 'last_session.json')

    def save_last_session(self, config: WatermarkConfig) -> None:
        path = self._last_session_path()
        data = config.to_dict()
        data['_meta'] = {
            'saved_at': datetime.utcnow().isoformat() + 'Z',
            'template_version': self.TEMPLATE_VERSION
        }
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def load_last_session(self) -> Optional[WatermarkConfig]:
        path = self._last_session_path()
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data.pop('_meta', None)
            return WatermarkConfig.from_dict(data)
        except Exception:
            return None

    # default template handling
    def _default_template_path(self) -> str:
        return os.path.join(self.config_dir, 'default_template.txt')

    def set_default_template(self, name: str) -> None:
        """Mark a template name as the default for startup.

        This writes a small text file containing the template name.
        """
        path = self._default_template_path()
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(name)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def get_default_template_name(self) -> Optional[str]:
        path = self._default_template_path()
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                name = f.read().strip()
            return name or None
        except Exception:
            return None

    def load_default_template(self) -> Optional[WatermarkConfig]:
        name = self.get_default_template_name()
        if not name:
            return None
        try:
            return self.load_template(name)
        except Exception:
            return None
