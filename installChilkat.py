import site, shutil, os

spList = site.getsitepackages()
print(spList)
spDir = spList[0]
if not "site-packages" in spDir:
  for d in spList:
    if "site-packages" in d:
      spDir = d
      break

if not os.path.exists(spDir):
  print("creating directory " + spDir)
  os.makedirs(spDir)

print("copying chilkat2.pyd to " + spDir)
shutil.copy("chilkat2.pyd",spDir)

print("The Chilkat Python module is ready to be used.")
print("Success.")
