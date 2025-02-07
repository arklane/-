import pandas as pd
import os

def pad_code(code):
    """将代码补足6位"""
    try:
        # 转换为字符串并删除空格
        code = str(code).strip()
        # 如果长度小于6,在前面补0
        return code.zfill(6)
    except:
        return code

def process_csv_files():
    """处理data目录下的所有CSV文件"""
    # 获取data目录路径
    data_dir = 'data'
    
    # 遍历data目录下的所有csv文件
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(data_dir, filename)
            
            try:
                # 读取CSV文件
                df = pd.read_csv(file_path)
                
                # 检查是否存在'代码'列
                if '代码' in df.columns:
                    # 对'代码'列应用补零函数
                    df['代码'] = df['代码'].apply(pad_code)
                    
                    # 保存回原文件
                    df.to_csv(file_path, index=False)
                    print(f"成功处理文件: {filename}")
                else:
                    print(f"文件 {filename} 中没有找到'代码'列")
                    
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")

if __name__ == "__main__":
    process_csv_files()