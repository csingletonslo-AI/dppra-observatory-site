from pathlib import Path
import sys, warnings, json
sys.path.insert(0,str(Path(__file__).parent/'packages'))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from checks import BASE, PAIRS, dump

def design(data,binary=False):
 x=pd.DataFrame({'Codex':(data.coder=='Codex').astype(float),'Gemini':(data.coder=='Gemini').astype(float)},index=data.index)
 dummy=pd.get_dummies(data.field,prefix='field',drop_first=True,dtype=float)
 x=pd.concat([x,dummy],axis=1)
 if binary:x.insert(0,'intercept',1.)
 assert np.linalg.matrix_rank(x.to_numpy())==x.shape[1]
 return x

def fit(data,label,cutoff=None):
 data=data.copy().reset_index(drop=True)
 dropped=[]
 if cutoff is not None:
  data['binary']=(data.rating>cutoff).astype(int)
  counts=data.groupby('field').binary.nunique()
  dropped=counts[counts<2].index.tolist()
  data=data[~data.field.isin(dropped)].reset_index(drop=True)
 x=design(data,binary=cutoff is not None)
 if cutoff is None:
  model=sm.OrdinalGEE(data.rating,x,groups=data.source_id,cov_struct=sm.cov_struct.Independence())
 else:
  model=sm.GEE(data.binary,x,groups=data.source_id,family=sm.families.Binomial(),cov_struct=sm.cov_struct.Independence())
 with warnings.catch_warnings(record=True) as caught:
  warnings.simplefilter('always')
  result=model.fit(maxiter=250,ctol=1e-8,cov_type='robust')
 g=data.source_id.nunique()
 cov=result.cov_params()*(g/(g-1))
 names=list(result.params.index)
 rows=[]
 for a,b in PAIRS:
  c=np.zeros(len(names))
  if a!='Claude':c[names.index(a)]+=1
  if b!='Claude':c[names.index(b)]-=1
  beta=float(c@result.params);se=float(np.sqrt(c@cov@c));crit=stats.t.ppf(.975,g-1)
  p=2*stats.t.sf(abs(beta/se),g-1)
  rows.append({'model':label,'contrast':a+' - '+b,'log_odds':beta,'se':se,'odds_ratio':np.exp(beta),'ci_low':np.exp(beta-crit*se),'ci_high':np.exp(beta+crit*se),'p':p,'documents':g,'fields':data.field.nunique(),'ratings':len(data)})
 for row,p in zip(rows,multipletests([r['p'] for r in rows],method='holm')[1]):row['p_holm']=p
 diag={'model':label,'converged':bool(result.converged),'iterations':len(result.fit_history['params']),'warnings':[str(w.message) for w in caught],'n_parameters':len(result.params),'covariance_rank':int(np.linalg.matrix_rank(cov)),'smallest_cov_eigenvalue':float(np.linalg.eigvalsh(cov).min()),'max_absolute_parameter':float(abs(result.params).max()),'threshold':cutoff,'fields_excluded_for_no_binary_variation':dropped}
 # Independently verify the working-independence estimating equation and the
 # document-cluster sandwich covariance, including expanded ordinal thresholds.
 X=np.asarray(model.exog);y=np.asarray(model.endog);mu=np.asarray(result.fittedvalues)
 residual=y-mu
 score=X.T@residual
 bread=np.linalg.inv(X.T@((mu*(1-mu))[:,None]*X))
 cluster_scores=np.array([X[model.groups==doc].T@residual[model.groups==doc] for doc in np.unique(model.groups)])
 sandwich=bread@(cluster_scores.T@cluster_scores)@bread
 diag['max_average_score']=float(abs(score).max()/len(y))
 diag['sandwich_max_difference']=float(abs(sandwich-result.cov_params().to_numpy()).max())
 indices=[names.index('Codex'),names.index('Gemini')]
 diag['coder_covariance_rank']=int(np.linalg.matrix_rank(cov.to_numpy()[np.ix_(indices,indices)]))
 assert diag['max_average_score']<1e-7,diag
 assert diag['sandwich_max_difference']<1e-5,diag
 assert diag['coder_covariance_rank']==2,diag
 result.params.to_csv(BASE/f'parameters_{label}.csv')
 (BASE/f'model_{label}.txt').write_text(result.summary().as_text()+'\n\nReported pairwise contrasts use robust covariance multiplied by G/(G-1) and t(G-1) reference, with Holm adjustment.\n',encoding='utf-8')
 print(label,diag,rows,flush=True)
 assert result.converged,(label,diag)
 assert np.isfinite(result.params).all() and np.isfinite(cov).all().all()
 assert all(np.isfinite(r['se']) and r['se']>0 for r in rows)
 return rows,diag

def main():
 data=pd.read_csv(BASE/'common_valid_ratings.csv')
 rows=[];diags=[]
 subsets=[('all_ordinal',data),('ethical_principles',data[data.field.str.startswith('eth_')])]
 subsets += [('without_'+sector,data[data.sector!=sector]) for sector in sorted(data.sector.unique())]
 for label,sub in subsets:
  out,diag=fit(sub,label);rows+=out;diags.append(diag)
  dump('ordinal_results.json',{'contrasts':rows,'diagnostics':diags})
 for cutoff in range(5):
  out,diag=fit(data,f'above_{cutoff}',cutoff);rows+=out;diags.append(diag)
  dump('ordinal_results.json',{'contrasts':rows,'diagnostics':diags})
 pd.DataFrame(rows).to_csv(BASE/'ordinal_contrasts.csv',index=False)

if __name__=='__main__':main()
