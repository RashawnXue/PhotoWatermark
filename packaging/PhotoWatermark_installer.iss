[Setup]
; PhotoWatermark Windows安装程序配置
AppName=PhotoWatermark
AppVersion=1.0.0
AppPublisher=PhotoWatermark Team
AppPublisherURL=https://github.com/your-repo/PhotoWatermark
AppSupportURL=https://github.com/your-repo/PhotoWatermark/issues
AppUpdatesURL=https://github.com/your-repo/PhotoWatermark/releases
DefaultDirName={autopf}\PhotoWatermark
DefaultGroupName=PhotoWatermark
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\README.md
OutputDir=..\dist
OutputBaseFilename=PhotoWatermark_Setup
SetupIconFile=..\assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "..\dist\PhotoWatermark\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 注意: 不要在任何共享系统文件上使用"Flags: ignoreversion"

[Icons]
Name: "{group}\PhotoWatermark"; Filename: "{app}\PhotoWatermark.exe"
Name: "{group}\{cm:UninstallProgram,PhotoWatermark}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\PhotoWatermark"; Filename: "{app}\PhotoWatermark.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\PhotoWatermark"; Filename: "{app}\PhotoWatermark.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\PhotoWatermark.exe"; Description: "{cm:LaunchProgram,PhotoWatermark}"; Flags: nowait postinstall skipifsilent

[Registry]
; 注册文件关联（可选）
Root: HKCR; Subkey: ".jpg"; ValueType: string; ValueName: ""; ValueData: "PhotoWatermark.Image"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".jpeg"; ValueType: string; ValueName: ""; ValueData: "PhotoWatermark.Image"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".png"; ValueType: string; ValueName: ""; ValueData: "PhotoWatermark.Image"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PhotoWatermark.Image"; ValueType: string; ValueName: ""; ValueData: "PhotoWatermark Image"; Flags: uninsdeletekey
Root: HKCR; Subkey: "PhotoWatermark.Image\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\PhotoWatermark.exe,0"
Root: HKCR; Subkey: "PhotoWatermark.Image\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\PhotoWatermark.exe"" ""%1"""

[Code]
// 检查.NET Framework或Visual C++ Redistributable
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // 检查Visual C++ Redistributable
  if not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64') then
  begin
    if MsgBox('此程序需要 Microsoft Visual C++ Redistributable。是否要下载并安装？', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://aka.ms/vs/17/release/vc_redist.x64.exe', '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
    end;
  end;
end;

// 卸载前清理
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // 清理用户数据（可选）
    if MsgBox('是否要删除用户配置和模板文件？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{userappdata}\PhotoWatermark'), True, True, True);
    end;
  end;
end;
