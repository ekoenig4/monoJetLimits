import os
from ROOT import TFile

process = { 'ZJets':2,'WJets':3,'DiBoson':4,'GJets':5,'TTJets':6,'DYJets':7,'QCD':8 }

def MakeShapeCard(mx,mv,systematics,dir,docat='sr'):
    with open("template_shape.txt","r") as template: temptext=template.readlines()
    rfile = TFile.Open(dir+'/'+systematics)
    dir = dir + '/Mx_'+mx
    if not os.path.isdir(dir): os.mkdir(dir)
    if not os.path.isdir(dir+'/template/'): os.mkdir(dir+'/template/')
    if docat == 'sr': category = ['sr']
    else:             category = ['sr','e','ee','m','mm']
    for cat in category:
        marked_for_removal = sorted( [ i for mc,i in process.items() if rfile.Get(cat+'/'+mc).Integral() == 0 ],reverse = True )
        newtext = [ line for line in temptext ]
        section = 0
        with open(dir+"/template/"+cat+".txt","w") as newshape:
            for i,line in enumerate(newtext):
                if line == '-----\n': section += 1; continue
                if 'file' in line: line = line.replace('file','../../'+systematics)
                if any(marked_for_removal):
                    words = line.split()
                    if len(words) > 2:
                        if section == 1:
                            for j in marked_for_removal: words.pop(j)
                        elif section == 2:
                            for j in marked_for_removal: words.pop(j+1)
                        string = ''
                        for word in words: string += word+' '
                        line = string + '\n'
                if cat == 'sr':
                    if 'bin1' in line: line = line.replace('bin1','sr')
                    if section == 1 and 'DM' in line: line = line.replace('DM','Mx'+mx+'_Mv'+mv)
                else:
                    if 'bin1' in line: line = line.replace('bin1',cat)
                    if section == 1:
                        words = line.split()
                        if len(words) > 2: words.pop(1)
                        string = ''
                        for word in words: string += word+' '
                        line= string+'\n'
                    elif section == 2:
                        words = line.split()
                        words.pop(2)
                        string = ''
                        for word in words: string += word+' '
                        line = string+'\n'
                newshape.write(line)
    ############################################################################################
    cwd = os.getcwd()
    os.chdir(dir)
    arg = 'combineCards.py sr=template/sr.txt '
    if docat != 'sr':
        for cat in ('e','ee','m','mm'): arg += cat+'=template/'+cat+'.txt '
    arg += '> zprimeMx'+mx+'_Mv'+mv+'_shape.txt'
    os.system(arg)
    os.chdir(cwd)
    rfile.Close()
##################################################################################
if __name__ == "__main__":
    MakeShapeCard('nan','nan','nan','.')
