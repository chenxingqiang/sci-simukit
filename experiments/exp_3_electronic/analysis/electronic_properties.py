#!/usr/bin/env python3
"""
实验3: 电子性质测量
测量带隙和迁移率随应变的变化
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

class ElectronicPropertiesAnalyzer:
    def __init__(self, data_dir="outputs"):
        self.data_dir = data_dir
        self.target_bandgap_range = [1.2, 2.4]  # eV
        self.target_mobility_range = [5.2, 21.4]  # cm²V⁻¹s⁻¹
        self.target_beta = 8.2  # 应变耦合参数
        self.tolerance = {"bandgap": 0.1, "mobility": 1.0, "beta": 0.5}
        
    def load_uv_vis_data(self, filename):
        """加载紫外-可见吸收光谱数据"""
        filepath = os.path.join(self.data_dir, 'uv_vis', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1]  # wavelength, absorbance
        
    def calculate_bandgap(self, wavelength, absorbance):
        """从吸收光谱计算带隙"""
        # 转换为能量
        energy = 1240 / wavelength  # eV
        
        # 计算(αhν)²
        alpha = absorbance / 1000  # 假设样品厚度1μm
        alpha_h_nu_squared = (alpha * energy) ** 2
        
        # 找到线性区域
        linear_region = (energy > 1.0) & (energy < 3.0)
        if np.sum(linear_region) < 10:
            return None
            
        # 线性拟合
        def linear_func(x, a, b):
            return a * x + b
            
        popt, pcov = curve_fit(linear_func, energy[linear_region], 
                              alpha_h_nu_squared[linear_region])
        
        # 带隙是x轴截距
        bandgap = -popt[1] / popt[0]
        return bandgap
        
    def load_hall_data(self, filename):
        """加载霍尔效应数据"""
        filepath = os.path.join(self.data_dir, 'hall_effect', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1], data[:, 2]  # field, voltage, current
        
    def calculate_mobility(self, field, voltage, current, thickness=1e-6):
        """从霍尔效应计算迁移率"""
        # 霍尔系数
        R_H = voltage / (field * current)
        
        # 载流子浓度
        n = 1 / (abs(R_H) * 1.6e-19)  # cm⁻³
        
        # 电导率
        sigma = current / (voltage * thickness)  # S/m
        
        # 迁移率
        mobility = sigma / (n * 1.6e-19)  # cm²V⁻¹s⁻¹
        
        return mobility, n
        
    def load_four_probe_data(self, filename):
        """加载四探针数据"""
        filepath = os.path.join(self.data_dir, 'four_probe', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1]  # voltage, current
        
    def calculate_resistivity(self, voltage, current, geometry_factor=1.0):
        """计算电阻率"""
        resistance = voltage / current
        resistivity = resistance * geometry_factor  # Ω·cm
        return resistivity
        
    def analyze_strain_response(self, strain_values, bandgaps, mobilities):
        """分析应变响应"""
        strains = np.array(strain_values)
        bandgaps = np.array(bandgaps)
        mobilities = np.array(mobilities)
        
        # 带隙随应变变化
        def linear_func(x, a, b):
            return a * x + b
            
        popt_bg, pcov_bg = curve_fit(linear_func, strains, bandgaps)
        
        # 迁移率随应变变化（指数关系）
        def exp_func(x, a, b, c):
            return a * np.exp(b * x) + c
            
        popt_mob, pcov_mob = curve_fit(exp_func, strains, mobilities)
        
        return {
            'bandgap_slope': popt_bg[0],
            'bandgap_intercept': popt_bg[1],
            'mobility_prefactor': popt_mob[0],
            'mobility_exponent': popt_mob[1],
            'mobility_offset': popt_mob[2],
            'r_squared_bandgap': self.calculate_r_squared(strains, bandgaps, popt_bg),
            'r_squared_mobility': self.calculate_r_squared(strains, mobilities, popt_mob)
        }
        
    def calculate_r_squared(self, x, y, params):
        """计算R²值"""
        if len(params) == 2:  # 线性拟合
            y_pred = params[0] * x + params[1]
        else:  # 指数拟合
            y_pred = params[0] * np.exp(params[1] * x) + params[2]
            
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot)
        
    def check_synergistic_effect(self, pristine_mobility, doped_mobility, strain_mobility, combined_mobility):
        """检查协同效应"""
        # 简单叠加预测
        additive_prediction = pristine_mobility + (doped_mobility - pristine_mobility) + (strain_mobility - pristine_mobility)
        
        # 协同增强因子
        synergy_factor = combined_mobility / additive_prediction
        
        return {
            'additive_prediction': additive_prediction,
            'actual_enhancement': combined_mobility,
            'synergy_factor': synergy_factor,
            'synergistic': synergy_factor > 1.5  # 协同效应>150%
        }
        
    def validate_results(self, bandgaps, mobilities, strain_response, synergy_analysis):
        """验证实验结果"""
        validation_results = {
            'bandgap_range_valid': False,
            'mobility_range_valid': False,
            'strain_coupling_valid': False,
            'synergistic_effect_valid': False,
            'overall_valid': False
        }
        
        # 验证带隙范围
        min_bg, max_bg = min(bandgaps), max(bandgaps)
        if (self.target_bandgap_range[0] <= min_bg <= self.target_bandgap_range[1] and
            self.target_bandgap_range[0] <= max_bg <= self.target_bandgap_range[1]):
            validation_results['bandgap_range_valid'] = True
            
        # 验证迁移率范围
        min_mob, max_mob = min(mobilities), max(mobilities)
        if (self.target_mobility_range[0] <= min_mob <= self.target_mobility_range[1] and
            self.target_mobility_range[0] <= max_mob <= self.target_mobility_range[1]):
            validation_results['mobility_range_valid'] = True
            
        # 验证应变耦合参数
        if abs(strain_response['mobility_exponent'] - self.target_beta) <= self.tolerance['beta']:
            validation_results['strain_coupling_valid'] = True
            
        # 验证协同效应
        if synergy_analysis['synergistic']:
            validation_results['synergistic_effect_valid'] = True
            
        # 总体验证
        validation_results['overall_valid'] = all([
            validation_results['bandgap_range_valid'],
            validation_results['mobility_range_valid'],
            validation_results['strain_coupling_valid'],
            validation_results['synergistic_effect_valid']
        ])
        
        return validation_results
        
    def save_results(self, bandgaps, mobilities, strain_response, synergy_analysis, validation_results):
        """保存分析结果"""
        results = {
            'bandgaps': bandgaps,
            'mobilities': mobilities,
            'strain_response': strain_response,
            'synergy_analysis': synergy_analysis,
            'validation_results': validation_results,
            'target_ranges': {
                'bandgap': self.target_bandgap_range,
                'mobility': self.target_mobility_range,
                'beta': self.target_beta
            }
        }
        
        with open('results/electronic_properties.json', 'w') as f:
            json.dump(results, f, indent=2)
            
    def plot_results(self, strain_values, bandgaps, mobilities, strain_response):
        """绘制分析结果"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        strains = np.array(strain_values)
        
        # 带隙随应变变化
        ax1.plot(strains, bandgaps, 'ro-', label='Experimental')
        ax1.axhspan(self.target_bandgap_range[0], self.target_bandgap_range[1], 
                   alpha=0.3, color='green', label='Target Range')
        ax1.set_xlabel('Strain (%)')
        ax1.set_ylabel('Band Gap (eV)')
        ax1.set_title('Band Gap vs Strain')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 迁移率随应变变化
        ax2.plot(strains, mobilities, 'bo-', label='Experimental')
        ax2.axhspan(self.target_mobility_range[0], self.target_mobility_range[1], 
                   alpha=0.3, color='green', label='Target Range')
        ax2.set_xlabel('Strain (%)')
        ax2.set_ylabel('Mobility (cm²V⁻¹s⁻¹)')
        ax2.set_title('Mobility vs Strain')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 紫外-可见吸收光谱示例
        wavelength = np.linspace(300, 800, 100)
        absorbance = np.exp(-(wavelength - 500)**2 / 10000) + 0.1 * np.random.randn(100)
        ax3.plot(wavelength, absorbance)
        ax3.set_xlabel('Wavelength (nm)')
        ax3.set_ylabel('Absorbance')
        ax3.set_title('UV-Vis Absorption Spectrum')
        ax3.grid(True, alpha=0.3)
        
        # 霍尔效应数据示例
        field = np.linspace(-1, 1, 50)
        voltage = 0.1 * field + 0.01 * np.random.randn(50)
        ax4.plot(field, voltage, 'g-')
        ax4.set_xlabel('Magnetic Field (T)')
        ax4.set_ylabel('Hall Voltage (V)')
        ax4.set_title('Hall Effect Measurement')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results/electronic_properties.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """主函数"""
    analyzer = ElectronicPropertiesAnalyzer()
    
    # 模拟数据（实际实验中从文件读取）
    strain_values = [-5.0, -2.5, 0.0, 2.5, 5.0]
    bandgaps = [1.85, 1.65, 1.45, 1.25, 1.15]  # eV
    mobilities = [5.2, 6.8, 8.7, 15.3, 21.4]  # cm²V⁻¹s⁻¹
    
    # 分析应变响应
    strain_response = analyzer.analyze_strain_response(strain_values, bandgaps, mobilities)
    
    # 分析协同效应
    synergy_analysis = analyzer.check_synergistic_effect(
        mobilities[2], mobilities[1], mobilities[3], mobilities[4]
    )
    
    # 验证结果
    validation_results = analyzer.validate_results(
        bandgaps, mobilities, strain_response, synergy_analysis
    )
    
    # 保存结果
    analyzer.save_results(bandgaps, mobilities, strain_response, synergy_analysis, validation_results)
    
    # 绘制结果
    analyzer.plot_results(strain_values, bandgaps, mobilities, strain_response)
    
    print("电子性质测量分析完成!")
    print(f"验证结果: {validation_results}")

if __name__ == "__main__":
    main()
