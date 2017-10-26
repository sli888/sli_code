import pandas as pd
import numpy as np

def stackcolumns (exfile, tabname, pat='IDL'):
    ex_data = pd.ExcelFile (exfile)
    df = ex_data.parse(tabname)
    idlcol = list (filter (lambda x: pat in x, df.columns))
    idl_stack= pd.melt(df.reset_index(), id_vars=['Lotno','WN', 'X', 'Y'], value_vars=idlcol, var_name='Label', value_name=pat)
    splitcol = idl_stack.Label.apply(lambda x: pd.Series(x.split('_')))
    if len(splitcol.columns) == 5:
        splitcol.columns = ['Vg_baise','Vds','FET_type','wxl','Other']

    if pat == 'MM':
        splitcol.columns = ['VTL_Name','Vds','other1','FET_type','wxl','MM12']
    if len(splitcol.columns) == 7:
        splitcol.columns = ['Vg_baise','Vds','FET_type','wxl','Other','other1', 'other2']
        
    splitwl = splitcol.wxl.apply(lambda x: pd.Series(x.replace('P','.').split('X')))
    splitwl.columns = ['w','l']
    return df, pd.concat([idl_stack, splitcol, splitwl], axis=1)

                    
def specvalidation (exfile, dfin, tabname='SPEC'):
    ex_data = pd.ExcelFile (exfile)
    spec = ex_data.parse(tabname)
    summarydf = pd.DataFrame()
    for col in dfin.columns:
        if sum(spec['Parameter']== col)>0:
            lsl= float(spec.loc[spec['Parameter']== col]['LSL_TV2'])
            usl= float(spec.loc[spec['Parameter']== col]['USL_TV2'])
            lpl= float(spec.loc[spec['Parameter']== col]['LPL_TV2'])
            upl= float(spec.loc[spec['Parameter']== col]['UPL_TV2'])
            newdf= pd.pivot_table (dfin, values =col, index=['Lotno', 'WN'], aggfunc=lambda x: x.size - sum( x.between(lsl , usl) )) 
            if summarydf.empty:
                summarydf = newdf
            else:
                summarydf = summarydf.merge(newdf, how='left', left_index = True, right_index= True )
    sum_stacked = summarydf.stack() #stack up the table and get total count
    sum_stacked = sum_stacked.to_frame('Total_Count')
    newdf= pd.pivot_table (sum_stacked, values='Total_Count', index=['Lotno', 'WN'], aggfunc=lambda x:sum(x))
    summarydf = summarydf.merge(newdf, how='left', left_index = True, right_index= True )
    summarydf = summarydf.stack()
    summarydf = summarydf.reset_index()
    summarydf = summarydf.rename(columns={'level_2':'Params', 0:'Counts'})
    summarydf = summarydf.pivot_table (values='Counts', index='Params', columns=['Lotno','WN'], aggfunc ='sum')
    summarydf['Total']= summarydf.sum(axis=1)
    summarydf = summarydf.sort_values('Total',ascending=False)
    return summarydf
                    
def clean_up (exfile, tabname):
    ex_data = pd.ExcelFile (exfile)
    df = ex_data.parse(tabname)
    return 1


def read_specs (exfile, tabname):
    ex_data = pd.ExcelFile (exfile)
    df = ex_data.parse(tabname)
    return 1
                    
def mergewithmaster (olddf, newdf, mgind=['Lotno', 'WN', 'X', 'Y']):
    outdf = olddf.merge(newdf, how='left', on=mgind)
    
    return outdf


def Leffcalc (df, w='10'):
    newdf=pd.DataFrame()
    for i, tdf  in df.groupby(['Lotno','WN', 'X', 'Y','Vg_baise']):
        l=list(tdf.loc[df['w']==w]['l'].apply (lambda x: float (x)))
        ron=list(tdf.loc[df['w']==w]['IDL'].apply (lambda x: 0.05/float (x)))
        fitout = np.polyfit (l,ron,  1)
        tmpdata = list (i)+ list(fitout)
        s = pd.Series(tmpdata, index=['Lotno','WN', 'X', 'Y','Vg_baise','a','b'])
        newdf = newdf.append (s, ignore_index=True)
    finaldf=pd.DataFrame()
    for i, tdf in newdf.groupby(['Lotno','WN', 'X', 'Y']):
        Leff=[]
        Leff+= [(float(tdf.loc[tdf['Vg_baise']=='IDL1']['b'])  - float(tdf.loc[tdf['Vg_baise']=='IDL2']['b']))/(float(tdf.loc[tdf['Vg_baise']=='IDL2']['a']) - float(tdf.loc[tdf['Vg_baise']=='IDL1']['a']))]
        Leff+= [(float(tdf.loc[tdf['Vg_baise']=='IDL1']['b'])  - float(tdf.loc[tdf['Vg_baise']=='IDL3']['b']))/(float(tdf.loc[tdf['Vg_baise']=='IDL3']['a']) - float(tdf.loc[tdf['Vg_baise']=='IDL1']['a']))]
        Leff+= [(float(tdf.loc[tdf['Vg_baise']=='IDL2']['b'])  - float(tdf.loc[tdf['Vg_baise']=='IDL3']['b']))/(float(tdf.loc[tdf['Vg_baise']=='IDL3']['a']) - float(tdf.loc[tdf['Vg_baise']=='IDL2']['a']))]
        leffa= np.average(Leff) # get the Average
        tmpdata = list (i)+ [leffa]
        s = pd.Series(tmpdata, index=['Lotno','WN', 'X', 'Y','Delta_L'])
        
        finaldf= finaldf.append (s, ignore_index=True)
    return newdf, finaldf 
    


def mmcoef (df, leff=0.02):
    newdf=pd.DataFrame()
    #newdf= pd.pivot_table (newdf, values ='MM', index=['Lotno', 'WN', 'w', 'l'], columns=['MM12'], aggfunc=lambda x:(np.percentile(x,75)-np.percentile(x,25))/1.35) 
    tmp1= pd.pivot_table (df, values ='MM', index=['Lotno', 'WN', 'w', 'l','X','Y'], columns=['MM12'])
    vt_delta= tmp1['M1'] -tmp1['M2'] 
    vt_f = vt_delta.to_frame('delta')
    newdf= pd.pivot_table (vt_f, values ='delta', index=['Lotno', 'WN', 'w', 'l'], aggfunc=lambda x:(np.percentile(x,75)-np.percentile(x,25))/1.35) 
    newdf['Sigma_IQR_Dvt'] = newdf['delta']
    finaldf=pd.DataFrame()
    
    for i, tdf  in newdf.groupby(['Lotno','WN']):
        tdf=tdf.reset_index()
        tdf=tdf.set_index(['Lotno','WN'])
        tdf['1/sqrt(w*leff)'] = tdf['w'].astype(float) * (tdf['l'].astype(float)- leff)
        tdf['1/sqrt(w*leff)'] = tdf['1/sqrt(w*leff)'].apply (lambda x: 1/x**(1/2))
        #we should not use polyfit instead we need to fix the intercept to be zero
        x = list (tdf['1/sqrt(w*leff)'])
        A=np.array([x, np.zeros(len(x))])
        y=np.array(list(tdf['delta']))
        

        fit = np.linalg.lstsq(A.T, y)[0]
        #fitout = np.polyfit (tdf['1/sqrt(w*leff)'], tdf['delta'],1)
        tdf['mm_coef'] = fit[0] 
        tdf['b'] = fit[1] 
        tdf['est'] = tdf['1/sqrt(w*leff)']*fit[0] + fit[1]

        tdf=tdf.reset_index()
        finaldf= finaldf.append (tdf, ignore_index=True)
         
    return finaldf
    



spec_file = 'H:\\Device development\\TSI\\Scripts\\perl\\pcm_specs.xls'

olddf, sdf = stackcolumns ('H:\Device development\TSI\Etest\PCM\Raw\_RG77V6983A_TV2_Prod_N5_9D_STD_PCM.xls', 'RawData', 'IDL')
summarydf = specvalidation (spec_file, olddf) 

olddfmm, sdfmm = stackcolumns ('H:\Device development\TSI\Etest\PCM\Raw\RG77V6983A_TV2_Match_N5_124D_MM_PCM.xls', 'RawData', 'MM')
tmp= mmcoef (sdfmm)
newdf, finaldf= Leffcalc (sdf)
merge1 = mergewithmaster (olddf, finaldf) 

mgind=['Lotno', 'WN']
merge2 = mergewithmaster (merge1, tmp, mgind)   #merge that with the PCM file 

sdf.to_csv('c:/temp/stacked.csv')
summarydf.to_csv('c:/temp/summary_spec.csv')
tmp.to_csv('c:/temp/mm.csv')
sdfmm.to_csv('c:/temp/stacked_mm.csv')
newdf.to_csv('c:/temp/delta_L_large.csv')
finaldf.to_csv('c:/temp/delta_L.csv')
merge1.to_csv('c:/temp/merge1.csv')
merge2.to_csv('c:/temp/merge2.csv')
