"""Portable RUN07 nominal sensitivity check, release 2026-09-14.
Requires numpy. Run from any directory. Results go in generated/ beside this script.
Paired sensitivity: complete triples per field; Pearson statistic calibrated by
within-document permutations of coder labels (exchangeability null, stronger
than marginal homogeneity alone). Monte Carlo plus-one p; Bonferroni over 17.
"""
from pathlib import Path
import ast, json, hashlib, math, itertools, csv
import numpy as np

BASE=Path(__file__).resolve().parent
OUT=BASE/'generated'
OUT.mkdir(exist_ok=True)
CODERS=['Claude','Codex','Gemini']
B=199999
SEED=20260914
FIELDS=['assessment_object_code', 'cb_balance_code', 'cb_benefit_evidence_label_code', 'cb_cost_evidence_label_code', 'cb_distribution_direction_code', 'cb_primary_cost_bearer_code', 'cb_primary_material_beneficiary_code', 'cb_primary_value_capturer_code', 'dominant_value_type_code', 'external_link_boundary_code', 'journal_level_of_analysis_code', 'journal_method_evidence_label_code', 'journal_method_type_code', 'journal_source_type_code', 'learner_posture_code', 'overall_dominant_valence_code', 'responsibility_concentration_code']
data={}
with (BASE/'nominal_inputs.csv').open(newline='',encoding='utf-8') as f:
 for row in csv.DictReader(f):
  key=(row['sector'],row['source_id'])
  for c in CODERS:
   data.setdefault(key,{}).setdefault(c,{})[row['field']]=None if row[c]=='' else int(row[c])
assert len(data)==65 and all(set(v)==set(CODERS) for v in data.values())

def clean(v):
 if v is None or v in (8,9): return None
 assert isinstance(v,(int,float)) and v==int(v),v
 return int(v)

def pearson(tab):
 tab=np.asarray(tab,float)
 tab=tab[:,tab.sum(axis=0)>0]
 expected=tab.sum(1)[:,None]*tab.sum(0)[None,:]/tab.sum()
 return float(np.sum((tab-expected)**2/expected)),expected

def sf_even(x,df):
 # Chi-square survival for positive even df, using the integer gamma identity.
 assert df>0 and df%2==0
 z=x/2
 return math.exp(-z)*sum(z**i/math.factorial(i) for i in range(df//2))

perms=np.array(list(itertools.permutations(range(3))))
results=[]; inputs=[]
for fi,field in enumerate(FIELDS):
 vals=[[clean(data[d][c].get(field)) for c in CODERS] for d in sorted(data)]
 cats=sorted({v for row in vals for v in row if v is not None})
 tab=np.array([[sum(row[c]==k for row in vals) for k in cats] for c in range(3)])
 orig,oe=pearson(tab);op=sf_even(orig,2*(len(cats)-1)) if len(cats)>1 else 1.
 # Preserve legacy 8/9 exclusion above for historical reproduction only.
 # Assessment object uses 88/99 missing; 8/9 are substantive categories.
 paired_vals=vals if field!='assessment_object_code' else [[None if data[d][c].get(field) in (None,88,99) else int(data[d][c][field]) for c in CODERS] for d in sorted(data)]
 complete=[row for row in paired_vals if all(v is not None for v in row)]
 for d in sorted(data): inputs.append({'sector':d[0],'source_id':d[1],'field':field,**{c:data[d][c].get(field) for c in CODERS}})
 ccats=sorted({v for row in complete for v in row}); n=len(complete);k=len(ccats)
 assert n>0
 a=np.array([[ccats.index(v) for v in row] for row in complete])
 ctab=np.stack([np.bincount(a[:,c],minlength=k) for c in range(3)])
 stat,ce=pearson(ctab)
 cp=sf_even(stat,2*(k-1)) if k>1 else 1.
 expected=ctab.sum(0)/3
 rng=np.random.default_rng(SEED+fi)
 exceed=0
 discordant=int(np.sum(np.any(a!=a[:,0,None],axis=1)))
 if discordant==0:
  exceed=B
 else:
  for start in range(0,B,2000):
   size=min(2000,B-start)
   choices=rng.integers(0,6,size=(size,n))
   shuffled=np.take_along_axis(np.broadcast_to(a,(size,n,3)),perms[choices],axis=2)
   counts=np.stack([(shuffled==v).sum(axis=1) for v in range(k)],axis=2)
   stats=(((counts-expected)**2)/expected).sum(axis=(1,2))
   exceed+=int(np.count_nonzero(stats>=stat-1e-10))
 p=(exceed+1)/(B+1)
 r={'field':field,'available_n_Claude':int(tab[0].sum()),'available_n_Codex':int(tab[1].sum()),'available_n_Gemini':int(tab[2].sum()),'complete_documents':n,'discordant_documents':discordant,'categories':k,'original_chi2':orig,'original_df':2*(len(cats)-1),'original_p':op,'original_bonferroni':min(1,op*17),'complete_chi2':stat,'complete_independent_p':cp,'paired_permutation_p':p,'paired_bonferroni':min(1,p*17),'exceedances':exceed,'permutations':B,'seed':SEED+fi,'expected_cells_below5':int((ce<5).sum()),'original_counts':tab.tolist(),'complete_counts':ctab.tolist(),'original_categories':cats,'complete_categories':ccats}
 results.append(r)
 print(field,n,round(orig,3),round(op,7),p,min(1,p*17),flush=True)

# Check published rounded values BEFORE interpreting the paired sensitivity.
published={'responsibility_concentration_code':37.0,'cb_distribution_direction_code':36.0,'cb_primary_cost_bearer_code':26.0,'cb_balance_code':15.3,'cb_cost_evidence_label_code':16.9}
for f,x in published.items():
 assert abs(next(r['original_chi2'] for r in results if r['field']==f)-x)<.051,(f,x)
payload={'numpy_version':np.__version__,'results':results}
(OUT/'nominal_results.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
for filename,rows in [('nominal_results.csv',[{k:v for k,v in r.items() if not isinstance(v,list)} for r in results]),('nominal_inputs.csv',inputs)]:
 with (OUT/filename).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Published five rounded chi-square values reproduced. Complete.',flush=True)

expected=json.loads((BASE/"nominal_results.json").read_text())["results"]
assert results==expected,"Results differ from released reference; check NumPy version and inputs."
print("All 17 results exactly match the released reference.")
