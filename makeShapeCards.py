import os

def MakeShapeCard(mx,mv,systematics,dir,docat='sr'):
    with open("template_shape.txt","r") as template: temptext=template.readlines()
    dir = dir + '/Mx_'+mx
    if not os.path.isdir(dir): os.mkdir(dir)
    if not os.path.isdir(dir+'/template/'): os.mkdir(dir+'/template/')
    if docat == 'sr': category = ['sr']
    else:             category = ['sr','e','ee','m','mm']
    for cat in category:
        newtext = [ line for line in temptext ]
        section = 0
        with open(dir+"/template/"+cat+".txt","w") as newshape:
            for line in newtext:
                if line == '-----\n': section += 1
                if 'file' in line: line = line.replace('file','../../'+systematics)
                if cat == 'sr':
                    if 'bin1' in line: line = line.replace('bin1','sr')
                    if section == 1 and 'DM' in line: line = line.replace('DM','Mx'+mx+'_Mv'+mv)
                    newshape.write(line)
                else:
                    if 'bin1' in line: line = line.replace('bin1',cat)
                    if section == 1:
                        words = line.split()
                        if len(words) == 9: words.pop(1)
                        string = ''
                        for word in words: string += word+' '
                        newshape.write(string+'\n')
                    elif section == 2:
                        words = line.split()
                        if len(words) == 10: words.pop(2)
                        string = ''
                        for word in words: string += word+' '
                        newshape.write(string+'\n')
                    else: newshape.write(line)
    ############################################################################################
    cwd = os.getcwd()
    os.chdir(dir)
    arg = 'combineCards.py sr=template/sr.txt '
    if docat != 'sr':
        for cat in ('e','ee','m','mm'): arg += cat+'=template/'+cat+'.txt '
    arg += '> zprimeMx'+mx+'_Mv'+mv+'_shape.txt'
    os.system(arg)
    os.chdir(cwd)
##################################################################################
if __name__ == "__main__":
    MakeShapeCard('nan','nan','nan','.')
