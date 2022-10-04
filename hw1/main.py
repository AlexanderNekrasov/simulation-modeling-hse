import pandas as pd

df = pd.read_csv('fns_for_model.csv', sep=';')

# get df by quarter (2021, 3rd quarter)
df_quarter = df[(df['year'] == 2021) & (df['quarter'] == 3)]

print(df_quarter[['employee_num', 'income', 'taxesVAT', 'insurance']].describe())

'''
       employee_num        income      taxesVAT     insurance
count  36824.000000  3.682400e+04  3.682400e+04  3.682400e+04
mean      42.382623  9.138794e+07  5.048732e+06  4.411725e+06
std      319.176895  1.212090e+09  8.671604e+07  4.419626e+07
min        0.000000  0.000000e+00  0.000000e+00  0.000000e+00
25%        1.000000  0.000000e+00  0.000000e+00  5.032240e+04
50%        4.000000  0.000000e+00  0.000000e+00  2.205971e+05
75%       17.333333  0.000000e+00  0.000000e+00  1.154227e+06
max    18019.333333  1.464221e+11  1.221386e+10  3.563453e+09
'''