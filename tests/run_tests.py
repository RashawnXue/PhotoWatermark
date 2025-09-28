#!/usr/bin/env python3
"""
测试运行脚本

运行所有测试用例
"""

import sys
import os
import unittest

# 添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_tests():
    """运行所有测试"""
    print("PhotoWatermark 测试运行器")
    print("=" * 50)
    
    # 运行单元测试
    print("\\n🧪 运行单元测试...")
    loader = unittest.TestLoader()
    unit_dir = os.path.join(os.path.dirname(__file__), 'unit')
    unit_suite = loader.discover(unit_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    unit_result = runner.run(unit_suite)
    
    # 运行集成测试
    print("\\n🔗 运行集成测试...")
    integration_dir = os.path.join(os.path.dirname(__file__), 'integration')
    if os.path.exists(integration_dir) and os.listdir(integration_dir):
        # 直接运行集成测试文件
        sys.path.insert(0, integration_dir)
        integration_suite = unittest.TestSuite()
        for filename in os.listdir(integration_dir):
            if filename.startswith('test_') and filename.endswith('.py'):
                module_name = filename[:-3]
                try:
                    module = __import__(module_name)
                    integration_suite.addTest(loader.loadTestsFromModule(module))
                except ImportError as e:
                    print(f"警告: 无法导入 {module_name}: {e}")
        
        integration_result = runner.run(integration_suite)
    else:
        print("没有找到集成测试文件")
        integration_result = unittest.TestResult()
        integration_result.wasSuccessful = lambda: True
    
    # 汇总结果
    total_success = unit_result.wasSuccessful() and integration_result.wasSuccessful()
    
    print("\\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"单元测试: {'✅ 通过' if unit_result.wasSuccessful() else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_result.wasSuccessful() else '❌ 失败'}")
    print(f"总体结果: {'✅ 全部通过' if total_success else '❌ 存在失败'}")
    
    return total_success
    

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
