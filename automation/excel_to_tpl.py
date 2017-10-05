#written by Shuyi Li 7/27/2017

import os
import numpy as np
import re
import pandas as pd
tpltemplate = "H:\Device development\TSI\Etest\Test Plans\TV2\Atm_TV2_template.tpl"
outtpl = 'H:\Device development\TSI\Etest\Test Plans\TV2\\'
exfile = "H:\\Device development\\TSI\\MaskSets\\TV2\\TV2_device_list_v10.xlsx"
#exfile=  "C:\\Users\\lishuyi\\Documents\\parser\\TV2_device_list_v9.xlsx"

def devmap(Vds, devname, W, L, N, F1, F2, S1, S2, ano,cath, gatepin, drainpin, sourcepin, subpin,algo): 
    devname=devname.upper()
    vdsV = '_5V_'+devname
    vgB = '7.5'
    vgswp_max = '10.0'

    Ids_pre = 300E-9
    IGLname = '7P5'
    normalids =  300E-9 
    p = re.compile (r'(\d+)([km])',re.I)
    Inf = 1E-6/100
    Ibv= 10E-6/(10+10)
    Ivf = -10E-6/100
    prevN = N
    m=p.search(str(N))
    relist =[]
    if m:
        if 'k' in m.group(2).lower():
          N=int(m.group(1))*1000
        if 'm' in m.group(2).lower():
          N=int(m.group(1))*1E6
    	  
    
    if Vds==1.8:
        vdsV = '_1P8V_'+devname
        vgB = '2.5'
        vgswp_max = '5.0'
        IGLname = '2P5'

    Xsiscon = 'Source={0:},Gate={1:},Drain={2:},Bulk={3:}'.format(sourcepin,gatepin,drainpin,subpin)
    CGG_str= 'L={0:},H1={1:},H2={2:},H3={3:},H4={4:}'.format(gatepin,subpin,sourcepin,drainpin,'49')
    CGC_str= 'H={0:},L1={1:},L2={2:},Gnd1={3:},Gnd2={4:}'.format(gatepin,sourcepin,drainpin,subpin,'49')
    HALL_str= 'Gate={0:},Body={1:},Drain={2:},Source={3:},Vp={4:},Vm={5:},Chk=49'.format(gatepin,subpin,F1,F2,S1,S2,'49')
    Tox_str= 'H1={0:},L={1:},L1={2:},Gnd1={3:},Gnd2={4:}'.format(gatepin,sourcepin,drainpin,subpin,'49')

    Area = W*L
    if re.search(r'SQ',devname):
         Area=  Area*1.1
         W = W*422.5/400

    Square= int(1)

    WLexpress ='W='+str(W)+',L='+str(L)
    
    if W>0 and L>0:
        Square= '{0:.3f}'.format(L/W)
        normalids = Ids_pre* W/L
        Inf = Inf*Area
        Ivf = Ivf*Area
        Ibv = Ibv*(W+L)
        if N>0:
            normalids = normalids*N
            Inf = Inf*N
            Ivf = Ivf*N
            Ibv = Ibv*N


                  #key  :         alg1,      algo2,   conditions,                                                                                                                , retuned registers ,                      pinconnection
    algodict =  {  'VTL':          ['`VT`:',   'Vth5B',   'Ids='+'{0:.3E}'.format(normalids)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',             '`VTL'+vdsV+'`',                            Xsiscon], 
                   'VTL10':        ['`VT`:',   'Vth5B',   'Ids='+'{0:.3E}'.format(normalids/10)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',          '`VTL10'+vdsV+'`',                          Xsiscon],
                   'SS100':        ['`VT`:',   'SSwing',  'Ids='+'{0:.3E}'.format(normalids/100)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',         '`VTL100'+vdsV+'`,`SS100'+vdsV+'`',         Xsiscon],
                   'VTL100':       ['`VT`:',   'Vth5B',  'Ids='+'{0:.3E}'.format(normalids/100)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',          '`VTL100'+vdsV+'`',                         Xsiscon],
                   'VTL1K':        ['`VT`:',   'Vth5B',  'Ids='+'{0:.3E}'.format(normalids/1000)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',         '`VTL1K'+vdsV+'`',                          Xsiscon],
                   'VTL10K':       ['`VT`:',   'Vth5B',  'Ids='+'{0:.3E}'.format(normalids/10000)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',        '`VTL10K'+vdsV+'`',                         Xsiscon],
                   'VTL100K':      ['`VT`:',   'Vth5B',  'Ids='+'{0:.3E}'.format(normalids/100000)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',       '`VTL100K'+vdsV+'`',                        Xsiscon],
                   'VTLRON':        ['`VT`:',   'Vth5B_Ids', 'Ids='+'{0:.3E}'.format(normalids)+',Vds=0.05,Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',           '`VTL'+vdsV+'`,`IDL1'+vdsV+'`,`IDL2'+vdsV+'`,`IDL3'+vdsV+'`', Xsiscon],
                   'VTS':          ['`VT`:',    'Vth5B', 'Ids='+'{0:.3E}'.format(normalids)+',Vds='+str(Vds)+',Vgstart=0.0,Vgstop=1.5,Back=2,Vgstep=0.0001,Delay=0.001',      '`VTS'+vdsV+'`',                              Xsiscon], 
                   'JDL':          ['`IDLIN`:' ,'Mos_Idsat_j' ,  'Vd=0.05,Vg='+str(Vds)+',Waittime=0.010,Id_comp=0.01,'+WLexpress,                                            '`JDL'+vdsV+'`',                               Xsiscon], 
                   'JGM':          ['`JG`:'    ,'GMMAX3_j'    ,  'Vmin=0.0,Vmax=2.0,Steps=41,Vds=0.05,Vbs=0.0,Intrange=2,Width=1,Length=1,Type="N",'+WLexpress,               '`JGM'+vdsV+'`',                               Xsiscon],                          
                   'JOFF' :        ['`ILD`:'   ,'D_ild_j'     ,  'Vd='+str(Vds)+',Delay=0.100,'+WLexpress,                                                                    '`JOFF'+vdsV+'`',                              Xsiscon],                      
                   'JSOFF':        ['`ILD`:'   ,'S_ild_j'     ,  'Vd='+str(Vds)+',Delay=0.100,'+WLexpress,                                                                    '`JSOFF'+vdsV+'`',                             Xsiscon],                                             
                   'JBOFF':        ['`ILD`:'   ,'B_ild_j'     ,  'Vd='+str(Vds)+',Delay=0.100,'+WLexpress,                                                                    '`JBOFF'+vdsV+'`',                             Xsiscon],                                          
                   'JDS':          ['`IDSAT`:' ,'Mos_Idsat_j' ,  'Vd='+str(Vds)+',Vg='+str(Vds)+',Waittime=0.010,Id_comp=0.1,'+WLexpress,                                     '`JDS'+vdsV+'`',                               Xsiscon],                                        
                   'NF':           ['`NF`:'    ,'D_ideal',      'Iforce2='+'{0:.3E}'.format(Inf)+',Iforce1='+'{0:.3E}'.format(Inf/10),                                        '`NF_'+devname+'`',                            'P1='+str(ano)+',P2='+str(cath)], 
                   'VF':           ['`VF`:'    ,'Bvi',          'Iforce='+'{0:.3E}'.format(Ivf)+',Delay=.020,V_comp=20.0',                                                    '`VF_'+devname+'`',                            'Pin1='+str(cath)+',Pin2='+str(ano)],
                   'BV':           ['`BV`:'    ,'Bvi',          'Iforce='+'{0:.3E}'.format(Ibv)+',Delay=.020,V_comp=30.0',                                                    '`BV_'+devname+'`',                            'Pin1='+str(cath)+',Pin2='+str(ano)],  
                   'LKG':          ['`ILK`:'   ,'Pn_akleak',    'Vforce=5.0,Ntim=1,Ndiv=1,Delay=0.200,Pos=1,Idd_comp=1E-2',                                                   '`LKG_'+devname+'`',                           'Pin1='+str(cath)+',Pin2='+str(ano)], 
                   'RES':          ['`R`:'    ,'Res',           'Vforce=0.05,Ntim=1,Delay=0.01,Ndiv='+str(Square),                                                            '`RES_'+devname+'`',                           'Pin1='+str(ano)+',Pin2='+str(cath)],  
                   'RS':           ['`R`:'    ,'Res',           'Vforce=0.05,Ntim=1,Delay=0.01,Ndiv='+str(Square),                                                            '`RS_'+devname+'`',                           'Pin1='+str(ano)+',Pin2='+str(cath)],  
                   'RSK':          ['`R_KEL`:','rk_kel',        'Iforce=-100.0E-6,Irange=100.E-6,Delay=0.1,Square='+str(Square),                                              '`RS_'+devname+'`',                            'Vmh='+str(S1)+',Vml='+str(S2)+',If='+str(F1)+',Gnd='+str(F2)],                                                                                                                                       
                   'RK':           ['`R_KEL`:','rk_kel',        'Iforce=-100.0E-6,Irange=100.E-6,Delay=0.1,Square='+str(Square),                                              '`RK_'+devname+'`',                            'Vmh='+str(S1)+',Vml='+str(S2)+',If='+str(F1)+',Gnd='+str(F2)],                                                                                                                                       
                   'RSV':          ['`RSVDP`:','R_vdp',         'Iforce=1E-4,Delay=0.05,Vno_comp=15',                                                                         '`RS_'+devname+'`',                           'Vh='+str(S1)+',Vl='+str(S2)+',Ih='+str(F1)+',Gnd='+str(F2)],                                                                                                                                       
                   'GLKG_2T':      ['`GLKG`:', 'ILg',            'Vg='+vgB+',Delay=0.100',                                                                                    '`ILG_'+devname+"_"+IGLname+'`',               'Source='+str(subpin)+',Gate='+str(gatepin)+',Drain='+str(subpin)+',Bulk='+str(subpin)+',Chk=49'],
                   'GLKG_2T_ACC':  ['`GLKG`:', 'ILg',            'Vg=-'+vgB+',Delay=0.100',                                                                                   '`ILG_ACC_'+devname+"_"+IGLname+'`',         'Source='+str(subpin)+',Gate='+str(gatepin)+',Drain='+str(subpin)+',Bulk='+str(subpin)+',Chk=49'],
                   'GLKG':         ['`GLKG`:', 'ILg',            'Vg='+vgB+',Delay=0.100',                                                                                    '`ILG_'+devname+"_"+IGLname+'`',               'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Bulk='+str(subpin)+',Chk=49'],
                   'GLKG_ACC':     ['`GLKG`:', 'ILg',            'Vg=-'+vgB+',Delay=0.100',                                                                                   '`ILG_ACC_'+devname+"_"+IGLname+'`',            'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Bulk='+str(subpin)+',Chk=49'],
                   'Probe_pad_check':      ['`Short`:', 'Probes_check_24',            'Vh=0.05,Delay=0.01',                                                                   '`PROBE_PAD_CHECK'+'`',                     'p1=1,p2=2,p3=3,p4=4,p5=5,p6=6,p7=7,p8=8,p9=9,p10=10,p11=11,p12=12,p13=13,p14=14,p15=15,p16=16,p17=17,p18=18,p19=19,p20=20,p21=21,p22=22,p23=23,p24=24,p25=25'],  
#sweep definition:

                   'TOXINV': ['`TOX`:','Cs3_i1'      ,  'freq=1E+5,sig_level=0.03,int_time=2,vstart='+str(Vds-0.01)+',vstop='+str(Vds+0.01)+',vstep=0.01,hold_time=0.1,Area='+str(Area)+',Cal=1,Conv=1',        '`TOXINV'+vdsV+'`',            Tox_str],                            
                   'IDVD':   ['`IDVD'+vdsV+'`:', 'M_1sweep_d',       'Vdstart=0,Vdstep=0.2,Vdstop=20,Fint=1,Id_comp=10E-03,Ig_comp=5E-03,Is_comp=10E-03,Ib_comp=10E-03,Vg=0',                                   '`IDVD'+vdsV+'`' ,            'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Body='+str(subpin)],        
                   'IGVG_INV':      ['`IGVG'+vdsV+'`:' , 'M_1sweep_g' ,        'Vgstart=0.0,Vgstop='+vgswp_max+',Vgstep=0.50,Vd=0.0,Fint=1,Id_comp=1E-01,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',            '`IGVG'+vdsV+'_INV`' ,           'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Body='+str(subpin)+',Chk=0,Nbl=0'],
                   'IGVG_ACC':      ['`IGVG'+vdsV+'`:' , 'M_1sweep_g' ,      'Vgstart=0.0,Vgstop=-'+vgswp_max+',Vgstep=-0.50,Vd=0.0,Fint=1,Id_comp=1E-01,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',            '`IGVG'+vdsV+'_ACC`' ,           'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Body='+str(subpin)+',Chk=0,Nbl=0'],
                   'IGVG_2T_INV':   ['`IGVG'+vdsV+'`:' , 'M_1sw_all' ,        'Vstart=0.0,Vstop='+vgswp_max+',Vstep=0.50,Fint=1,Vs=0,I_comp=1E-5,Delay=0.01,Save=1,Fmode=1,Tie=0',                              '`IGVG'+vdsV+'_INV`' ,         'High='+str(gatepin)+',Low1='+str(subpin)+',Chk=0' ],
                   'IGVG_2T_ACC':   ['`IGVG'+vdsV+'`:' , 'M_1sw_all' ,        'Vstart=0.0,Vstop=-'+vgswp_max+',Vstep=-0.50,Fint=1,Vs=0,I_comp=1E-5,Delay=0.01,Save=1,Fmode=1,Tie=0',                            '`IGVG'+vdsV+'_ACC`' ,         'High='+str(gatepin)+',Low1='+str(subpin)+',Chk=0' ],
                   'IDVGK_a':['`IDVGK'+vdsV+'`:', 'M_1sweep_g_mv2',  'Vgstart=0.0,Vgstop=2.0,Vgstep=0.05,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01,'+WLexpress,                    '`IDVGK'+vdsV+'_a`',           'Gate='+str(gatepin)+',Body='+str(subpin)+',Drain='+str(F1)+',Source='+str(F2)+",Vp="+str(S1)+',Vm='+str(S2)],
                   'IDVGK_b':['`IDVGK'+vdsV+'`:', 'M_1sweep_g_mv2',  'Vgstart=2.0,Vgstop=7.0,Vgstep=0.20,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01,'+WLexpress,                    '`IDVGK'+vdsV+'_b`',           'Gate='+str(gatepin)+',Body='+str(subpin)+',Drain='+str(F1)+',Source='+str(F2)+",Vp="+str(S1)+',Vm='+str(S2)],
                   
                   'IDVG_a': ['`IDVG'+vdsV+'`:' , 'M_1sweep_g' ,      'Vgstart=0.0,Vgstop=2.0,Vgstep=0.05,Vd=0.05,Fint=1,Id_comp=1E-01,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                              '`IDVG'+vdsV+'_a`' ,           'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Body='+str(subpin)+',Chk=0,Nbl=0'],
                   'IDVG_b': ['`IDVG'+vdsV+'`:' , 'M_1sweep_g' ,      'Vgstart=2.0,Vgstop=7.0,Vgstep=0.50,Vd=0.05,Fint=1,Id_comp=1E-01,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                              '`IDVG'+vdsV+'_b`' ,           'Source='+str(sourcepin)+',Gate='+str(gatepin)+',Drain='+str(drainpin)+',Body='+str(subpin)+',Chk=0,Nbl=0'],

                   
                   'CGG0V':  ['`CGG'+vdsV+'`:',    'Csrs_sweep_vg', 'Vgstart=-0.01,Vgstop=+0.01,Vgstep=0.01,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1,Reverse=1',                                '`CGG'+vdsV+'_a`',              CGG_str],                     
                   'CGC0V':  ['`CGC'+vdsV+'`:',    'Csrs_sweep_l',  'Vgstart=-0.01,Vgstop=+0.01,Vgstep=0.01,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1',                                          '`CGC'+vdsV+'_b`' ,             CGC_str],

                   'CGG_a':  ['`CGG'+vdsV+'`:',    'Csrs_sweep_vg', 'Vgstart=+2.0,Vgstop=+5.0,Vgstep=0.10,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1,Reverse=1',                                  '`CGG'+vdsV+'_a`',              CGG_str],                     
                   'CGG_b':  ['`CGG'+vdsV+'`:',    'Csrs_sweep_vg', 'Vgstart=-2.0,Vgstop=+2.0,Vgstep=0.05,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1,Reverse=1',                                  '`CGG'+vdsV+'_b`',              CGG_str],                     
                   'CGG_c':  ['`CGG'+vdsV+'`:',    'Csrs_sweep_vg', 'Vgstart=-7.0,Vgstop=-2.0,Vgstep=0.10,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1,Reverse=1',                                  '`CGG'+vdsV+'_c`',              CGG_str],                     

                   'CGC_a':  ['`CGC'+vdsV+'`:',    'Csrs_sweep_l',  'Vgstart=-5.0,Vgstop=-2.0,Vgstep=0.10,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1',                                            '`CGC'+vdsV+'_a`' ,             CGC_str],
                   'CGC_b':  ['`CGC'+vdsV+'`:',    'Csrs_sweep_l',  'Vgstart=-2.0,Vgstop=+2.0,Vgstep=0.05,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1',                                            '`CGC'+vdsV+'_b`' ,             CGC_str],
                   'CGC_c':  ['`CGC'+vdsV+'`:',    'Csrs_sweep_l',  'Vgstart=+2.0,Vgstop=+7.0,Vgstep=0.10,freq=1E+5,sig_level=0.03,int_time=2,hold_time=0.1,Conv=1',                                            '`CGC'+vdsV+'_c`' ,             CGC_str],
                   'VDP_a': ['`IDVG'+vdsV+'_HALL_R2134`:', 'M_1sweep_g_mv', 'Vgstart=0.0,Vgstop=2.0,Vgstep=0.05,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R2134_a`',   HALL_str],  
                   'VDP_b': ['`IDVG'+vdsV+'_HALL_R2134`:', 'M_1sweep_g_mv', 'Vgstart=2.0,Vgstop=7.0,Vgstep=0.10,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R2134_b`',   HALL_str],  
                   'VDP_c': ['`IDVG'+vdsV+'_HALL_R3241`:', 'M_1sweep_g_mv', 'Vgstart=0.0,Vgstop=2.0,Vgstep=0.05,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R3241_a`',   HALL_str],  
                   'VDP_d': ['`IDVG'+vdsV+'_HALL_R3241`:', 'M_1sweep_g_mv', 'Vgstart=2.0,Vgstop=7.0,Vgstep=0.10,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R3241_b`',   HALL_str],  
                   'VDP_e': ['`IDVG'+vdsV+'_HALL_R4312`:', 'M_1sweep_g_mv', 'Vgstart=0.0,Vgstop=2.0,Vgstep=0.05,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R4312_a`',   HALL_str],  
                   'VDP_f': ['`IDVG'+vdsV+'_HALL_R4312`:', 'M_1sweep_g_mv', 'Vgstart=2.0,Vgstop=7.0,Vgstep=0.10,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R4312_b`',   HALL_str],  
                   'VDP_g': ['`IDVG'+vdsV+'_HALL_R1423`:', 'M_1sweep_g_mv', 'Vgstart=0.0,Vgstop=2.0,Vgstep=0.05,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R1423_a`',   HALL_str],  
                   'VDP_h': ['`IDVG'+vdsV+'_HALL_R1423`:', 'M_1sweep_g_mv', 'Vgstart=2.0,Vgstop=7.0,Vgstep=0.10,Vd=0.05,Fint=1,Id_comp=1E-02,Ig_comp=1E-05,Is_comp=1E-01,Ib_comp=1E-01',                       '`IDVG'+vdsV+'_HALL_R1423_b`',   HALL_str],  
                   
                 }

#    for i in algodict.keys(): 
#       print (i)
#       for j in algodict[i]:
#          print (j)

# loopthrough all the keys
    for thiskey in sorted(algodict.keys()):
        if algo == thiskey:   #exactly match
            relist = relist + [algodict[thiskey]]
        else:    #capture boundles
           p = re.compile(r'^(\w+)_[a-z]$')
           m = p.search (thiskey)
           if m: 
               if algo == m.group(1):
                   relist = relist + [algodict[thiskey]]


    if len(relist)>0:
          return relist
    else:
          return 0


#devmap (5.0, 10, 400, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,"QS_NFET_400X10")

#def devmap(Vds, devname, W, L, N, F1, F2, S1, S2, ano,cath, gatepin, drainpin, sourcepin, subpin): 
def parsexcel (ex_data, tpltype,vdsglob,flowtab):
    wantcol = ['Name',  'W', 'L', 'N',  'F1 (If)', 'F2 (Gnd)', 'S1 (Vmh)', 'S2 (Vml)', 'A', 'C', 'G', 'D', 'S', 'Sub (B)' ]
    intcol = [ 'F1 (If)', 'F2 (Gnd)', 'S1 (Vmh)', 'S2 (Vml)', 'A', 'C', 'G', 'D', 'S', 'Sub (B)' ]
    df = ex_data.parse(flowtab)
    finallist =[]
    colmatch = 'PCM_'
    if tpltype == "PCM":
        colmatch = 'PCM_'
    else:
        colmatch = 'SWP_'
    for i,row in df.iterrows():
       skiprow =0
       if row['Vds'] == '1P8V' and vdsglob == 5:
           skiprow=1
           print ("Skipping ", row ['Name'])
       if row['Vds'] == '5V' and vdsglob == 1.8:
           skiprow=1
           print ("Skipping ", row ['Name'])
       if skiprow != 1:
           for j in [col for col in df.columns if colmatch in col]:
               if pd.notnull(row[j]):
                     thisalgo = row[j].strip()
                     for inj  in intcol:
                         if type (row[inj])  is float and str(float(row[inj])).lower() != 'nan':
                             row[inj] = int(row[inj])
                     otherparam = list(row[wantcol])
                     otherparam.append(thisalgo) 
                     otherparam.insert(0,vdsglob) 


                     p = re.compile (r'([\w\d]+)_MM',re.I)
                     m = p.search(thisalgo)

                     if m:
                         algo_strip = m.group(1)
                         mm=[[],[]]
                         count = 0
                         for k in otherparam:
                             if ',' in str(k):
                                  mm[0].append(k.split(',')[0])
                                  mm[1].append(k.split(',')[1])
                             elif count == 1:   # the Device name
                                  mm[0].append(k+'_M1')
                                  mm[1].append(k+'_M2')
                             elif count == len(otherparam)-1:   #  algo needs to be stripped
                                  mm[0].append(algo_strip)
                                  mm[1].append(algo_strip)
                             else:
                                  mm[0].append(k)
                                  mm[1].append(k)
                             count = count +1

                         ct=1
                         for y in mm:
                             thislist = devmap(*y) 
                             if isinstance (thislist, list):
                                 if len(thislist[0])>0:
                                     for i in thislist:
                                          i[0]= '`'+row['Module Name/Label'].strip()+'`::'+i[0] 
                                          finallist = finallist + [i]
                             else:
                                 print ("No alo returns: "+ str(y))
                             ct=ct+1


#                     print ("working on algo "+row[['Name', 'W']])
                     else:
                         thislist = devmap(*otherparam) 
                         if isinstance (thislist, list):
                             if len(thislist[0])>0:
                                     for i in thislist:
                                          i[0]= '`'+row['Module Name/Label'].strip()+'`::'+i[0] 
                                          finallist = finallist + [i]
                         else:
                             print ("No alo returns: "+ str(otherparam))
    return finallist 

    


def writetpl (thislist, tpltype,coord,outname):
     maxsize={}
     l=0
     for i in thislist:
         if isinstance(i, list):
            k=0
            for j in i:
                if k not in maxsize.keys():
                    maxsize[k] = 0
                if len(j)>maxsize[k]:
                    maxsize[k]=len(j)
                k=k+1
         l=l+1     
     
     
     outformat=""
     outformatline=""
     
     for i in maxsize.keys():
         outformat = outformat + '{'+str(i)+':<'+str(maxsize[i])+'} '
         outformatline = outformatline + '{0:-<'+str(maxsize[i])+'} '
     


     mapline = '           `MODULE`            '
     F = open (tpltemplate,'r')
     outfile = open (outtpl+outname+'.tpl','w')
     for line in F:
         if '<replace algo>' in line:
              outfile.write('$'+outformatline.format('-')+"\n")
              outfile.write(" BODY\n")
              for i in thislist:
                  outfile.write(" "+outformat.format(*i)+"\n")
              outfile.write('$'+outformatline.format('-')+"\n")

         elif '<replace shots>' in line:
              for i in coord:
                  outfile.write(mapline+i+"\n")
         else:
              outfile.write(line)
              
     
     outfile.close()
     F.close()



def parsemaster  (exfile, tabname):
    ex_data = pd.ExcelFile (exfile)
    df = ex_data.parse(tabname)
    keycol = ['Flow Tab', 'Vds', 'Map Tab', 'TPL Type', 'Output Name'] 

    for i,row in df.iterrows():
        if 'x' in str(row['Crunch']):
            #make sure all the key columns is not null
                if row[keycol].isnull().sum() == 0:
                     Vds = row['Vds']
                     flowtab = row['Flow Tab']
                     maptab = row['Map Tab'] 
                     tpltype = row['TPL Type'] 
                     outname = row['Output Name'] 
                     if '1P8' in str(row['Vds']):
                          Vds=1.8
                     Vds = float(Vds)
                     if flowtab in ex_data.sheet_names and maptab in ex_data.sheet_names:
                          thislist    = parsexcel (ex_data, tpltype, Vds, flowtab)
                          coord = parsemap (ex_data,maptab)
                          writetpl (thislist, tpltype, coord,outname)
    return 1

                    

def parsemap  (ex_data,maptab):
    df = ex_data.parse(maptab)
    coord = []
    for i,row  in df.iterrows():
        for j in row.index:
            p = re.compile(r'[a-z]\d', re.I)
            if  p.search(str(row[j])):
                 coord = coord+[str(i+1)+","+str(j)]
    return coord

    
#for i in thislist:
#    print (outformat.format(*i))

# run that damn thing
thislist    = parsemaster (exfile, "TPL_Master")
