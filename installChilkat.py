import sys, site, shutil, os, platform

bGlobalInstall = False

if len(sys.argv) > 1:
    opt = sys.argv[1]
    if opt == '-g':
        bGlobalInstall = True
        print("Installing globally...\n")

if bGlobalInstall:
    spList = site.getsitepackages()
    print(spList)
    spDir = spList[0]
    if not "site-packages" in spDir:
        # prefer the first directory having "site-packages" in the name.
        for d in spList:
            if "site-packages" in d:
                spDir = d
                break
else:
    spDir = site.getusersitepackages()

if not os.path.exists(spDir):
    print("creating directory " + spDir)
    os.makedirs(spDir)

shutil.copy("chilkat2.pyd",spDir)

print("Success.")




