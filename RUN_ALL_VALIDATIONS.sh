#!/bin/bash
#
# 运行所有实验验证的便捷脚本
# 
# 使用方法:
#   ./RUN_ALL_VALIDATIONS.sh
#
# 或:
#   bash RUN_ALL_VALIDATIONS.sh
#

set -e  # 遇到错误立即退出

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🔬 富勒烯应变掺杂研究 - 本地实验验证                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目录: $SCRIPT_DIR"
echo ""

# 检查Python环境
echo "🔍 检查Python环境..."
if [ -d "fullerene-env" ]; then
    echo "✅ 找到虚拟环境: fullerene-env"
    source fullerene-env/bin/activate
else
    echo "⚠️  未找到虚拟环境，使用系统Python"
fi

# 检查Python版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "🐍 Python版本: $PYTHON_VERSION"
echo ""

# 检查关键依赖
echo "📦 检查依赖包..."
python -c "
import sys
missing = []
for package in ['numpy', 'pandas', 'ase', 'matplotlib']:
    try:
        __import__(package)
        print(f'  ✅ {package}')
    except ImportError:
        print(f'  ❌ {package} (缺失)')
        missing.append(package)
        
if missing:
    print(f'\n⚠️  缺少依赖: {", ".join(missing)}')
    print('请运行: pip install -r requirements.txt')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 依赖检查失败，请安装缺失的包"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 开始运行验证实验..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 进入experiments目录
cd experiments

# 选择运行方式
echo "选择运行方式:"
echo "  1. 运行所有实验（自动化，推荐）"
echo "  2. 运行综合验证框架"
echo "  3. 逐个运行实验（调试用）"
echo ""
echo -n "请选择 [1-3，默认1]: "

# 如果是自动化运行（no terminal），使用默认选项
if [ -t 0 ]; then
    read -r choice
else
    choice=1
    echo "1 (自动选择)"
fi

choice=${choice:-1}

case $choice in
    1)
        echo ""
        echo "🔬 运行所有实验（自动化模式）..."
        echo ""
        python run_local_validation_all.py
        ;;
    2)
        echo ""
        echo "🔬 运行综合验证框架..."
        echo ""
        python comprehensive_validation_framework.py
        ;;
    3)
        echo ""
        echo "🔬 逐个运行实验..."
        echo ""
        
        for exp in exp_1_structure exp_2_doping exp_3_electronic exp_4_polaron exp_5_synergy exp_6_optimal; do
            if [ -d "$exp" ]; then
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "运行: $exp"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                cd "$exp"
                python run_*_experiment.py || echo "⚠️  $exp 失败"
                cd ..
                echo ""
            else
                echo "⚠️  跳过: $exp (目录不存在)"
            fi
        done
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

# 返回根目录
cd "$SCRIPT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 验证完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 查看结果:"
echo "  - 主报告: experiments/local_validation_results/LOCAL_VALIDATION_REPORT.md"
echo "  - 数据摘要: experiments/local_validation_results/validation_summary.json"
echo "  - 运行日志: experiments/local_validation.log"
echo ""
echo "📖 详细文档:"
echo "  - experiments/RUN_VALIDATION_GUIDE.md"
echo ""
echo "🎯 下一步:"
echo "  1. 查看验证报告"
echo "  2. 根据结果更新论文"
echo "  3. 准备HPC计算"
echo "  4. 对接实验验证"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

