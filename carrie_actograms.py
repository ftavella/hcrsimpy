import numpy as np
import scipy as sp
from scipy.integrate import *
import pylab as plt
from math import *
import sys
from sets import Set
import pandas as pd
from scipy import interpolate
from actogram import *
from circular_stats import *
from LightSchedule import *
from singlepop_model_melatonin_carrie import *
from stroboscopic import *
from MelatoninSchedule import *


def EntrainTime(shift, MelatoninTime):
    """Put in a light and melatonin schedule and get out reentrainment time"""
    duration=16.0 #gets 8 hours of sleep
    intensity=150.0
    wake=6.0
    LightFunReg=lambda t: RegularLightSimple(t,intensity,wake,duration)

    MelatoninTime+=10*24.0
    Mel=lambda t: threeMelPulse(t, timePulse=MelatoninTime)
    
    #Create SP Model
    a=SinglePopModel(LightFunReg, Mel)
    init=a.integrateTransients()
    ent_angle=a.integrateModel(24*40, initial=init);
    tsdf=a.getTS()

    dlmo_func=sp.interpolate.interp1d(np.array(tsdf['Phase']), np.array(tsdf['Time']), bounds_error=False)

    real_days=tsdf['Time'].iloc[-1]/24.0
    num_days=ceil(tsdf['Time'].iloc[-1]/24.0)
        
    if (tsdf.Phase.iloc[0]<1.309):
        dlmo_phases=np.arange(1.309, real_days*2.0*sp.pi, 2*sp.pi) #all the dlmo phases using 1.309 as the cicadian phase of the DLMO
        dlmo_times=np.array(map(lambda x: fmod(x,24.0), np.array(map(dlmo_func, dlmo_phases))))
        dlmo_times= dlmo_times[np.isfinite(dlmo_times)]
        dayYvalsDLMO=num_days-np.arange(0.5, len(dlmo_times)+0.5, 1.0)
    else:
        dlmo_phases=np.arange(1.309+2*sp.pi, real_days*2.0*sp.pi, 2*sp.pi) #all the dlmo phases using 1.309 as the cicadian phase of the DLMO
        dlmo_times=np.array(map(lambda x: fmod(x,24.0), np.array(map(dlmo_func, dlmo_phases))))
        dlmo_times= dlmo_times[np.isfinite(dlmo_times)]
        dayYvalsDLMO=num_days-np.arange(1.5, len(dlmo_times)+1.5, 1.0)

    if (tsdf.Phase.iloc[0]<sp.pi):
        cbt_phases=np.arange(sp.pi, real_days*2.0*sp.pi, 2*sp.pi)
        cbt_times=np.array(map(lambda x: fmod(x,24.0), np.array(map(dlmo_func, cbt_phases))))
        cbt_times=cbt_times[np.isfinite(cbt_times)]
        dayYvalsCBT=num_days-(np.arange(0.5, len(cbt_times)+0.5, 1.0))
    else:
        cbt_phases=np.arange(sp.pi+2*sp.pi, real_days*2.0*sp.pi, 2*sp.pi)
        cbt_times=np.array(map(lambda x: fmod(x,24.0), np.array(map(dlmo_func, cbt_phases))))
        cbt_times=cbt_times[np.isfinite(cbt_times)]
        dayYvalsCBT=num_days-np.arange(1.5, len(cbt_times)+1.5, 1.0)

    delta_dlmo=np.diff(dlmo_times)
    reentrain_time=0
    passed_shift=False
    for d in delta_dlmo:
        if abs(d)>0.1:
            passed_shift=True
        if passed_shift==True and abs(d)<0.01:
            reentrain_time+=1
            break
        else:
            reentrain_time+=1

    return(reentrain_time-10)
    
        
        

    
    

def actogramRegularLightMel(MelatoninTime=96.0):
    """Show the effect of a regular light schedule on the circadian clock"""

    duration=16.0 #gets 8 hours of sleep
    intensity=150.0
    wake=6.0
    LightFunReg=lambda t: RegularLightSimple(t,intensity,wake,duration)

    Mel=lambda t: threeMelPulse(t, timePulse=MelatoninTime)
    
    #Create SP Model
    a=SinglePopModel(LightFunReg, Mel)
    init=a.integrateTransients()
    ent_angle=a.integrateModel(24*40, initial=init);
    tsdf=a.getTS()
    plt.figure()
    ax=plt.gca()
    acto=actogram(ax, tsdf) #add an actogram to those axes
    acto.addMarker(MelatoninTime)

    plt.title('Entrainment under Regular Light Conditions with Melatonin Pulse')
    plt.tight_layout()
    plt.show()

def JetLagActogram(shift, MelatoninTime=8.0):
    """Simulate the circadian rhythms of a slam shift in the light schedule. By default this will for a fully entrained subject and the shift will occur on the 11th day. MelatoninTime gives the time of day 
    on the 11th day that the first dose of melatonin is taken
    JetLagActogram(shift)

    """

    if (shift<0.0):
        print "Simulating westbound travel by ", abs(shift), " time zones"
    else:
        print "Simulating eastbound travel by ", abs(shift), " time zones"

    MelatoninTime+=10*24.0
        
    LightFunReg=lambda t: RegularLightSimple(t,150.0, 8.0,16.0)
    JetLag=lambda t: SlamShift(t, shift)
    Mel=lambda t: threeMelPulse(t, timePulse=MelatoninTime)
    
    #Create SP Model
    a=SinglePopModel(LightFunReg, Mel)
    init=a.integrateTransients()
    a.Light=JetLag
    ent_angle=a.integrateModel(24*40, initial=init);
    tsdf=a.getTS()
    plt.figure()
    ax=plt.gca()
    acto=actogram(ax, tsdf) #add an actogram to those axes
    acto.addMarker(MelatoninTime)
    
    plt.figure()
    ax=plt.gca()
    strobo=stroboscopic(ax, tsdf[tsdf['Time']>=10*24.0])
    
    plt.show()



    

if __name__=='__main__':
    #JetLagActogram(8.0, MelatoninTime=8.0)
    #actogramRegularLightMel(112.6)
    print EntrainTime(8.0, 8.0)
