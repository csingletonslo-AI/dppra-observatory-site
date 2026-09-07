from checks import BASE, dump
import numpy as np, pandas as pd, json
from scipy import stats
means=pd.read_csv(BASE/'document_means_all_ordinal.csv')
rep=json.loads((BASE/'reproduction.json').read_text())
ordres=json.loads((BASE/'ordinal_results.json').read_text())
S=means[['Claude','Codex','Gemini']].cov().to_numpy(); C=np.eye(3)-np.ones((3,3))/3
CS=C@S@C; epsilon=np.trace(CS)**2/(2*np.trace(CS@CS))
check={'greenhouse_geisser_epsilon':epsilon,'corrected_df1':2*epsilon,'corrected_df2':128*epsilon,'corrected_p':stats.f.sf(rep['anova']['F'],2*epsilon,128*epsilon),'max_sandwich_discrepancy':max(d['sandwich_max_difference'] for d in ordres['diagnostics']),'max_average_score':max(d['max_average_score'] for d in ordres['diagnostics'])}
dump('reproduced_verification.json',check)
print(check)
