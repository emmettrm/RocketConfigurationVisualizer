# -*- coding: utf-8 -*-
import numpy as np
import subprocess,os

def runCEA(filename):
    filename_no_extension = (filename.split('.inp')[0]).split('/')[1]
    subprocess.Popen('cp '+filename+' CEA+FORTRAN/.',shell = True).wait()
    cwd = os.getcwd()
    os.chdir('CEA+FORTRAN')
    p = subprocess.Popen(['./FCEA2'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data = p.communicate(input=filename_no_extension.encode())[0]
    subprocess.Popen('mv '+filename_no_extension+'.out ../CEAoutput/.',shell = True).wait() 
    subprocess.Popen('rm '+filename_no_extension+'.inp',shell = True).wait()
    os.chdir(cwd)

def readPropCEA(prop,t,p,fuel,oxid,of,prefix='benchmark'):
    """
    write a script that gives either gamma or cp?
    """
    filename = 'CEAoutput/'+prefix+'_'+str(t)+'_'+str(p)+'_'+str(fuel)+'_'+oxid+'_'+str(of)+'.out'
    filename = filename.replace('(','').replace(')','')
    f = open(filename,'r')

    if prop == 'gama':
        while True:
            line = f.readline()
            if 'GAMMAs' in line:
                gama = float(line.split(' ')[-1][:-1])
                break
        f.close()
        return gama
    if prop == 'cp':
        while True:
            line = f.readline()
            if 'WITH FROZEN REACTIONS' in line:
                f.readline()
                line = f.readline()
                cp = round(float(line.split(' ')[-1][:-1])*1000,1)
                break
        f.close()
        return cp

def calcPropCEA(t,p,fuel,oxid,of,prefix='benchmark'):
    filename = 'CEAoutput/'+prefix+'_'+str(t)+'_'+str(p)+'_'+str(fuel)+'_'+oxid+'_'+str(of)+'.inp'
    filename = filename.replace('(','').replace(')','')

    if os.path.isfile(filename):
        return
        
    if not os.path.exists('CEAoutput'):
        os.mkdir('CEAoutput')
    f = open(filename,'w')
    f.write('problem case=1 tp\n')
    f.write('  p(bar) = '+str(p)+'\n')
    f.write('  t(k) = '+str(t)+'\n')
    f.write('reac\n')
    f.write('  fuel='+str(fuel)+' wt=1\n')
    f.write('  oxid='+str(oxid)+' wt='+str(of)+'\n')
    f.write('output\n')
    f.write('  siunits short, transport\n')
    f.write('  t gam cp\n')
    f.write('end\n')
    f.close()
    runCEA(filename)

def calcPropStagnationCEA(p,fuel,oxid,of,prefix='benchmark'):
    filename = 'CEAoutput/'+prefix+'_'+str(p)+'_'+str(fuel)+'_'+oxid+'_'+str(of)+'_rkt.inp'
    filename = filename.replace('(','').replace(')','')

    if os.path.isfile(filename):
        return

    if not os.path.exists('CEAoutput'):
        os.mkdir('CEAoutput')
    f = open(filename,'w')
    f.write('problem    o/f='+str(of)+',\n')
    f.write('    rocket  fac   ac/at=1  tcest,k=3800\n')
    f.write('  p,bar='+str(p)+',\n')
    f.write('react  \n')
    f.write('  fuel='+str(fuel)+' \n')
    f.write('  oxid='+str(oxid)+' \n')
    f.write('output  transport \n')
    f.write('end\n')
    f.close()
    runCEA(filename)

def readPropStagnationCEA(prop,p,fuel,oxid,of,prefix='benchmark'):
    """
    write a code that gets stagnation values from cea and stores them in dictionary(if memory becomes an issue use files)
    """


    filename = 'CEAoutput/'+prefix+'_'+str(p)+'_'+str(fuel)+'_'+oxid+'_'+str(of)+'_rkt.out'
    filename = filename.replace('(','').replace(')','')
    f = open(filename,'r')

    if prop == 't':
        while True:
            line = f.readline()
            if 'T, K' in line:
                t = float(line.split('  ')[-3])
                break
        f.close()
        return t
    if prop == 'cp':
        while True:
            line = f.readline()
            if 'WITH FROZEN REACTIONS' in line:
                f.readline()
                line = f.readline()
                cp = round(float(line.split('  ')[-3])*1000,1)
                break
        f.close()
        return cp
    if prop == 'pr':
        while True:
            line = f.readline()
            if 'WITH FROZEN REACTIONS' in line:
                f.readline()
                f.readline()
                f.readline()
                line = f.readline()
                pr = float(line.split('  ')[-3])
                break
        f.close()
        return pr
    if prop == 'mi':
        while True:
            line = f.readline()
            if 'VISC,MILLIPOISE' in line:
                mi = float(line.split('  ')[-3])/1000
                break
        f.close()
        return mi