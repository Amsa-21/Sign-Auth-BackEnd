import site, shutil, os

spDir = site.getusersitepackages()

if not os.path.exists(spDir):
    print("creating directory " + spDir)
    os.makedirs(spDir)

shutil.copy("chilkat2.pyd",spDir)

print("Success.")




