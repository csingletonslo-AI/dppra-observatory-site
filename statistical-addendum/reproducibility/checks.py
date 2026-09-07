from pathlib import Path
import sys, json, hashlib, importlib.util, itertools, platform
sys.path.insert(0,str(Path(__file__).parent/'packages'))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from scipy import stats
import scipy, statsmodels, krippendorff
from statsmodels.stats.multitest import multipletests

BASE=Path(__file__).resolve().parent
CODERS=['Claude','Codex','Gemini']
PAIRS=[('Codex','Claude'),('Gemini','Claude'),('Codex','Gemini')]

def dump(name,obj):
 (BASE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=lambda x: x.item() if hasattr(x,'item') else str(x)),encoding='utf-8')

def load():
 long=pd.read_csv(BASE/'ordinal_ratings.csv')
 assert len(long)==5655
 assert not long.duplicated(['source_id','coder','field']).any()
 assert long.rating.dropna().isin(range(6)).all()
 wide=long.pivot(index=['source_id','sector','field'],columns='coder',values='rating')[CODERS]
 common=wide.dropna()
 common_long=common.reset_index().melt(id_vars=['source_id','sector','field'],value_vars=CODERS,var_name='coder',value_name='rating')
 common_long['rating']=common_long.rating.astype(int)
 assert len(common)==1727 and len(common_long)==5181
 common_long.to_csv(BASE/'common_valid_ratings.csv',index=False)
 audit=json.loads((BASE/'data_audit.json').read_text())
 return wide,common,common_long,audit


def rm_anova(means):
 x=means[CODERS].to_numpy();n,k=x.shape;grand=x.mean()
 total=np.sum((x-grand)**2); ss_doc=k*np.sum((x.mean(1)-grand)**2)
 ss_coder=n*np.sum((x.mean(0)-grand)**2);ss_error=total-ss_doc-ss_coder
 F=(ss_coder/(k-1))/(ss_error/((n-1)*(k-1)))
 return {'n_documents':n,'means':means[CODERS].mean().to_dict(),'F':F,'df1':k-1,'df2':(n-1)*(k-1),'p':stats.f.sf(F,k-1,(n-1)*(k-1)),'partial_eta_squared':ss_coder/(ss_coder+ss_error),'ss_coder':ss_coder,'ss_error':ss_error,'ss_total':total}

def doc_tests(common,label):
 means=common.groupby(level=['source_id','sector']).mean()
 rows=[]
 for a,b in PAIRS:
  d=(means[a]-means[b]).to_numpy();n=len(d);se=stats.sem(d);t,p=stats.ttest_1samp(d,0)
  ci=stats.t.interval(.95,n-1,loc=d.mean(),scale=se)
  rows.append({'analysis':label,'contrast':a+' - '+b,'n_documents':n,'mean_difference':d.mean(),'ci_low':ci[0],'ci_high':ci[1],'t':t,'df':n-1,'p':p,'positive_docs':int((d>1e-12).sum()),'tied_docs':int((abs(d)<=1e-12).sum()),'negative_docs':int((d < -1e-12).sum())})
 for row,p in zip(rows,multipletests([r['p'] for r in rows],method='holm')[1]):row['p_holm']=p
 means.to_csv(BASE/f'document_means_{label}.csv')
 return rows

def rank_tests(common,label):
 rng=np.random.default_rng(20260907)
 rows=[]
 for a,b in PAIRS:
  cell=np.sign(common[a]-common[b]);d=cell.groupby(level=['source_id','sector']).mean().to_numpy();n=len(d)
  # One bootstrap unit is a whole document; all its field and coder ratings travel together.
  boot=d[rng.integers(0,n,size=(30000,n))].mean(1)
  hi=int((d>1e-12).sum());lo=int((d < -1e-12).sum());ties=n-hi-lo
  p=stats.binomtest(hi,hi+lo,p=.5).pvalue if hi+lo else 1
  rows.append({'analysis':label,'contrast':a+' - '+b,'mean_net_higher_fraction':d.mean(),'ci_low':np.quantile(boot,.025),'ci_high':np.quantile(boot,.975),'higher_docs':hi,'tied_docs':ties,'lower_docs':lo,'sign_test_p':p,'higher_cells':int((cell>0).sum()),'tied_cells':int((cell==0).sum()),'lower_cells':int((cell<0).sum())})
 for row,p in zip(rows,multipletests([r['sign_test_p'] for r in rows],method='holm')[1]):row['sign_test_p_holm']=p
 return rows

def main():
 wide,common,long,audit=load()
 print('AUDIT',audit,flush=True)
 means=common.groupby(level=['source_id','sector']).mean()
 anova=rm_anova(means)
 pooled=[]
 for a,b in PAIRS:
  pair=wide[[a,b]].dropna();d=pair[a]-pair[b];t,p=stats.ttest_rel(pair[a],pair[b])
  pooled.append({'contrast':a+' - '+b,'n':len(pair),'mean_difference':d.mean(),'t':t,'p':p})
 alpha=krippendorff.alpha(reliability_data=wide[CODERS].to_numpy().T,level_of_measurement='ordinal')
 reproduction={'anova':anova,'pooled_pairs':pooled,'ordinal_alpha':alpha}
 dump('reproduction.json',reproduction);print('REPRODUCTION',reproduction,flush=True)
 assert abs(anova['F']-197.6)<.15,anova
 assert abs(anova['partial_eta_squared']-.755)<.001
 assert [p['n'] for p in pooled]==[1727,1727,1728]
 assert abs(alpha-.725)<.0006
 docs=[];ranks=[]
 for label,subset in [('all_ordinal',common),('ethical_principles',common[common.index.get_level_values('field').str.startswith('eth_')])]:
  docs+=doc_tests(subset,label);ranks+=rank_tests(subset,label)
 pd.DataFrame(docs).to_csv(BASE/'document_level_tests.csv',index=False)
 pd.DataFrame(ranks).to_csv(BASE/'rank_only_checks.csv',index=False)
 dump('sensitivity_results.json',{'document_level':docs,'rank_only':ranks})
 print('DOCUMENT TESTS',docs,flush=True);print('RANK CHECKS',ranks,flush=True)

if __name__=='__main__':main()
