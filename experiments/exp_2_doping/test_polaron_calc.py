#!/usr/bin/env python3
"""
快速测试极化子结合能计算
只测试 pristine C60
"""

from calculate_polaron_binding import PolaronBindingCalculator
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🧪 快速测试: Pristine C60 极化子结合能计算")
    logger.info("="*70)
    logger.info("目标: λ = 0.10-0.13 eV (论文参考值)")
    logger.info("="*70)
    
    calculator = PolaronBindingCalculator()
    
    # 只测试pristine C60
    result = calculator.calculate_polaron_binding_energy('pristine', 0.05)
    
    logger.info("\n" + "="*70)
    logger.info("📊 测试结果")
    logger.info("="*70)
    
    if result['status'] == 'success':
        electron = result.get('electron_polaron', {})
        lambda_e = electron.get('lambda_eV', 'N/A')
        
        logger.info(f"\n✅ 计算成功!")
        logger.info(f"   电子极化子结合能: λ_e = {lambda_e:.4f} eV")
        logger.info(f"   论文参考值: λ = 0.10-0.13 eV")
        
        if isinstance(lambda_e, float):
            if 0.08 <= lambda_e <= 0.15:
                logger.info(f"   ✅ 结果在合理范围内!")
            else:
                logger.warning(f"   ⚠️ 结果偏离参考值")
        
        if 'hole_polaron' in result:
            hole = result['hole_polaron']
            lambda_h = hole.get('lambda_eV', 'N/A')
            logger.info(f"   空穴极化子结合能: λ_h = {lambda_h:.4f} eV")
    else:
        logger.error(f"\n❌ 计算失败: {result.get('status')}")
    
    return result

if __name__ == "__main__":
    main()

