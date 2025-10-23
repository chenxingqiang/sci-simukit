#!/usr/bin/env python3
"""
实验5: 协同效应定量验证
定量验证三个协同效应的贡献
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
from pathlib import Path

class SynergisticEffectAnalyzer:
    def __init__(self, data_dir="outputs"):
        self.data_dir = data_dir
        self.target_factors = {
            'f_deloc': 1.8,      # 离域化因子
            'f_coupling': 1.8,   # 耦合增强因子
            'f_reorg': 1.5,      # 重组能因子
            'f_total': 8.75      # 总增强因子
        }
        self.tolerance = 0.2  # ±20%
        
    def load_hall_effect_data(self, filename):
        """加载变温霍尔效应数据"""
        filepath = os.path.join(self.data_dir, 'hall_effect', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1], data[:, 2]  # temperature, mobility, concentration
        
    def calculate_delocalization_factor(self, temperature, mobility):
        """计算离域化因子"""
        # 基于温度依赖的迁移率变化
        # 离域化程度越高，温度依赖越弱
        
        # 拟合温度依赖关系
        def temp_dep_func(T, A, B, C):
            return A * np.exp(-B / (T + C))
            
        try:
            popt, pcov = curve_fit(temp_dep_func, temperature, mobility,
                                 p0=[max(mobility), 100, 50])
            
            # 计算温度系数
            T_ref = 300  # K
            mobility_ref = temp_dep_func(T_ref, *popt)
            mobility_high_T = temp_dep_func(T_ref + 100, *popt)
            
            temp_coefficient = (mobility_high_T - mobility_ref) / mobility_ref
            
            # 离域化因子（温度系数越小，离域化越强）
            f_deloc = 1.0 / (1.0 + abs(temp_coefficient))
            
            return f_deloc
            
        except:
            return 1.0
            
    def load_magnetoresistance_data(self, filename):
        """加载磁阻数据"""
        filepath = os.path.join(self.data_dir, 'magnetoresistance', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1]  # field, resistance
        
    def calculate_coupling_enhancement_factor(self, field, resistance):
        """计算耦合增强因子"""
        # 基于磁阻行为判断耦合强度
        # 强耦合导致负磁阻，弱耦合导致正磁阻
        
        R_0 = resistance[np.argmin(np.abs(field))]  # 零场电阻
        magnetoresistance = (resistance - R_0) / R_0
        
        # 计算磁阻斜率
        field_abs = np.abs(field)
        valid_indices = field_abs > 0.1  # 避免零场附近的数据
        
        if np.sum(valid_indices) < 5:
            return 1.0
            
        slope = np.polyfit(field_abs[valid_indices], 
                          magnetoresistance[valid_indices], 1)[0]
        
        # 耦合增强因子（负斜率表示强耦合）
        f_coupling = 1.0 + abs(slope) * 10  # 经验公式
        
        return min(f_coupling, 3.0)  # 限制最大值
        
    def load_dielectric_data(self, filename):
        """加载介电常数数据"""
        filepath = os.path.join(self.data_dir, 'dielectric', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1]  # frequency, dielectric_constant
        
    def calculate_reorganization_factor(self, frequency, dielectric_constant):
        """计算重组能因子"""
        # 基于介电常数频率依赖计算重组能
        # 重组能越低，介电响应越快
        
        # 拟合介电常数频率依赖
        def dielectric_func(freq, eps_inf, eps_s, tau):
            return eps_inf + (eps_s - eps_inf) / (1 + (2 * np.pi * freq * tau)**2)
            
        try:
            popt, pcov = curve_fit(dielectric_func, frequency, dielectric_constant,
                                 p0=[3.0, 10.0, 1e-12])
            
            eps_inf, eps_s, tau = popt
            
            # 重组能因子（响应时间越短，重组能越低）
            f_reorg = 1.0 / (1.0 + tau * 1e12)  # 归一化因子
            
            return f_reorg
            
        except:
            return 1.0
            
    def load_photoluminescence_data(self, filename):
        """加载光致发光数据"""
        filepath = os.path.join(self.data_dir, 'photoluminescence', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1]  # wavelength, intensity
        
    def calculate_quantum_efficiency(self, wavelength, intensity):
        """计算量子效率"""
        # 积分发光强度
        total_intensity = np.trapz(intensity, wavelength)
        
        # 归一化量子效率
        quantum_efficiency = total_intensity / max(intensity) / len(wavelength)
        
        return quantum_efficiency
        
    def analyze_synergistic_effects(self, strain_values, doping_values, 
                                   f_deloc_values, f_coupling_values, f_reorg_values):
        """分析协同效应"""
        strains = np.array(strain_values)
        doping = np.array(doping_values)
        f_deloc = np.array(f_deloc_values)
        f_coupling = np.array(f_coupling_values)
        f_reorg = np.array(f_reorg_values)
        
        # 计算总增强因子
        f_total_values = f_deloc * f_coupling * f_reorg
        
        # 分析各因子的贡献
        contributions = {
            'delocalization': np.mean(f_deloc),
            'coupling': np.mean(f_coupling),
            'reorganization': np.mean(f_reorg),
            'total': np.mean(f_total_values)
        }
        
        # 分析协同效应强度
        synergy_strength = np.mean(f_total_values) / (np.mean(f_deloc) * 
                                                    np.mean(f_coupling) * 
                                                    np.mean(f_reorg))
        
        return {
            'contributions': contributions,
            'synergy_strength': synergy_strength,
            'f_total_values': f_total_values.tolist()
        }
        
    def validate_synergistic_effects(self, f_deloc, f_coupling, f_reorg, f_total):
        """验证协同效应"""
        validation_results = {
            'delocalization_valid': False,
            'coupling_valid': False,
            'reorganization_valid': False,
            'total_enhancement_valid': False,
            'synergistic_valid': False,
            'overall_valid': False
        }
        
        # 验证离域化因子
        if abs(f_deloc - self.target_factors['f_deloc']) <= self.tolerance:
            validation_results['delocalization_valid'] = True
            
        # 验证耦合增强因子
        if abs(f_coupling - self.target_factors['f_coupling']) <= self.tolerance:
            validation_results['coupling_valid'] = True
            
        # 验证重组能因子
        if abs(f_reorg - self.target_factors['f_reorg']) <= self.tolerance:
            validation_results['reorganization_valid'] = True
            
        # 验证总增强因子
        if abs(f_total - self.target_factors['f_total']) <= self.tolerance:
            validation_results['total_enhancement_valid'] = True
            
        # 验证协同效应（总因子大于各因子乘积）
        if f_total > f_deloc * f_coupling * f_reorg:
            validation_results['synergistic_valid'] = True
            
        # 总体验证
        validation_results['overall_valid'] = all([
            validation_results['delocalization_valid'],
            validation_results['coupling_valid'],
            validation_results['reorganization_valid'],
            validation_results['total_enhancement_valid'],
            validation_results['synergistic_valid']
        ])
        
        return validation_results
        
    def save_results(self, f_deloc, f_coupling, f_reorg, f_total, 
                    synergy_analysis, validation_results):
        """保存分析结果"""
        results = {
            'synergistic_factors': {
                'f_deloc': f_deloc,
                'f_coupling': f_coupling,
                'f_reorg': f_reorg,
                'f_total': f_total
            },
            'synergy_analysis': synergy_analysis,
            'validation_results': validation_results,
            'target_factors': self.target_factors
        }
        
        with open('results/synergistic_effects.json', 'w') as f:
            json.dump(results, f, indent=2)
            
    def plot_results(self, strain_values, doping_values, f_deloc_values, 
                    f_coupling_values, f_reorg_values, f_total_values):
        """绘制分析结果"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        strains = np.array(strain_values)
        doping = np.array(doping_values)
        
        # 离域化因子
        ax1.plot(strains, f_deloc_values, 'ro-', label='f_deloc')
        ax1.axhline(y=self.target_factors['f_deloc'], color='r', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Strain (%)')
        ax1.set_ylabel('Delocalization Factor')
        ax1.set_title('Delocalization Factor vs Strain')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 耦合增强因子
        ax2.plot(strains, f_coupling_values, 'bo-', label='f_coupling')
        ax2.axhline(y=self.target_factors['f_coupling'], color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Strain (%)')
        ax2.set_ylabel('Coupling Enhancement Factor')
        ax2.set_title('Coupling Enhancement Factor vs Strain')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 重组能因子
        ax3.plot(strains, f_reorg_values, 'go-', label='f_reorg')
        ax3.axhline(y=self.target_factors['f_reorg'], color='r', linestyle='--', alpha=0.5)
        ax3.set_xlabel('Strain (%)')
        ax3.set_ylabel('Reorganization Factor')
        ax3.set_title('Reorganization Factor vs Strain')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 总增强因子
        ax4.plot(strains, f_total_values, 'mo-', label='f_total')
        ax4.axhline(y=self.target_factors['f_total'], color='r', linestyle='--', alpha=0.5)
        ax4.set_xlabel('Strain (%)')
        ax4.set_ylabel('Total Enhancement Factor')
        ax4.set_title('Total Enhancement Factor vs Strain')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results/synergistic_effects.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """主函数"""
    analyzer = SynergisticEffectAnalyzer()
    
    # 模拟数据（实际实验中从文件读取）
    strain_values = [-5.0, -2.5, 0.0, 2.5, 5.0]
    doping_values = [2.5, 5.0, 7.5, 5.0, 5.0]  # 固定掺杂浓度
    f_deloc_values = [1.2, 1.4, 1.6, 1.8, 1.8]
    f_coupling_values = [1.3, 1.5, 1.7, 1.8, 1.8]
    f_reorg_values = [1.2, 1.3, 1.4, 1.5, 1.5]
    f_total_values = [1.87, 2.73, 3.81, 4.86, 4.86]
    
    # 分析协同效应
    synergy_analysis = analyzer.analyze_synergistic_effects(
        strain_values, doping_values, f_deloc_values, f_coupling_values, f_reorg_values
    )
    
    # 验证协同效应
    validation_results = analyzer.validate_synergistic_effects(
        f_deloc_values[-1], f_coupling_values[-1], f_reorg_values[-1], f_total_values[-1]
    )
    
    # 保存结果
    analyzer.save_results(
        f_deloc_values[-1], f_coupling_values[-1], f_reorg_values[-1], f_total_values[-1],
        synergy_analysis, validation_results
    )
    
    # 绘制结果
    analyzer.plot_results(
        strain_values, doping_values, f_deloc_values, f_coupling_values, 
        f_reorg_values, f_total_values
    )
    
    print("协同效应定量验证分析完成!")
    print(f"验证结果: {validation_results}")

if __name__ == "__main__":
    main()
