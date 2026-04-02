#
# AccessOwnership post-processing script for NZBGet
#

import os
import sys
import re
import pwd
import grp

# Exit codes used by NZBGet
SCRIPT_SUCCESS=93
SCRIPT_ERROR=94

# Debug messages from Extension
CHECK_SETTINGS="Check instructions in the extension settings"

# Check if all required script config options are present in config file
required_options = ('NZBPO_DESTDIR', 'NZBPO_ACCESS', 'NZBPO_OWNER', 'NZBPO_GROUP', 'NZBPO_OVERRIDEID')
for optname in required_options:
    if (optname not in os.environ):
        print(f"[ERROR] Option {optname[6:]} is missing in configuration file. Please check script settings")
        sys.exit(SCRIPT_ERROR)

# Check if the script is executed from settings page with a custom command
command = os.environ.get("NZBCP_COMMAND")
detect_mode = command == "Detect"
test_mode = command == "Test"
if command is not None and not any((detect_mode,test_mode)):
    print('[ERROR] Invalid command ' + command)
    sys.exit(SCRIPT_ERROR)

# Override and debugging
overrideid = os.environ['NZBPO_OVERRIDEID'];

# Detecting users Owner[UID] and Group[GID], executed from settings page
if detect_mode:
    try:
        if pwd.getpwuid(os.getuid())[2] is not None:
            print("User UID is detected:",[pwd.getpwuid(os.getuid())[2]],)
        else:
            print("Cannot detect logged in users UID")
            check = SCRIPT_ERROR

        if pwd.getpwuid(os.getuid())[3] is not None:
            print("Group GID is detected:",[pwd.getpwuid(os.getuid())[3]],)
        else:
            print("Cannot detect logged in users GID")
            check = SCRIPT_ERROR

        try:
            check
        except NameError: 
            sys.exit(SCRIPT_SUCCESS)
        else:
            sys.exit(check)
    except KeyError:
        print("The requested key was not found.")

# Counters for added Categories
countcategory = 1
for i in range(1, 100):
    if os.environ.get("NZBOP_Category" + str(i) + ".Name") is not None:
        countcategory +=1
countcategoryext = 1
for i in range(1, 100):
    if os.environ.get("NZBPO_CategoryExt" + str(i) + ".Name") is not None:
        countcategoryext +=1

# Testing the validity of settings, executed from settings page
if test_mode:
    if not os.environ.get("NZBPO_DestDir") == os.environ.get("NZBOP_DestDir"):
        print("Default Category: Invalid Path:",[os.environ.get("NZBPO_DestDir")],CHECK_SETTINGS)
        check = SCRIPT_ERROR
    if not re.match('^[0-7]{3}$', os.environ.get("NZBPO_Access")):
        print("Default Category: Invalid Access[mask]:",[os.environ.get("NZBPO_Access")],CHECK_SETTINGS)
        check = SCRIPT_ERROR

    if not re.match('^[0-9]{1,}$', os.environ.get("NZBPO_Owner")):
        print("Default Category: Invalid Owner[UID]:",[os.environ.get("NZBPO_Owner")],CHECK_SETTINGS)
        check = SCRIPT_ERROR
    else:
        try:
            pwd.getpwuid(int(os.environ.get("NZBPO_Owner")))
        except KeyError:
            if overrideid == "yes":
                print("Default Category: Invalid Owner[UID]:",[os.environ.get("NZBPO_Owner")],"<- ENABLED!!")
            else:
                print("Default Category: Invalid Owner[UID]:",[os.environ.get("NZBPO_Owner")],"User not in system.",CHECK_SETTINGS)
                check = SCRIPT_ERROR

    if not re.match('^[0-9]{1,}$', os.environ.get("NZBPO_Group")):
        print("Default Category: Invalid Group[GID]:",[os.environ.get("NZBPO_Group")],CHECK_SETTINGS)
        check = SCRIPT_ERROR
    else:
        try:
            grp.getgrgid(int(os.environ.get("NZBPO_Group")))
        except KeyError:
            if overrideid == "yes":
                print("Default Category: Invalid Group[GID]:",[os.environ.get("NZBPO_Group")],"<- ENABLED!!")
            else:
                print("Default Category: Invalid Group[GID]:",[os.environ.get("NZBPO_Group")],"Group not in system.",CHECK_SETTINGS)
                check = SCRIPT_ERROR

    for i in range(1, countcategoryext):
        if os.environ.get("NZBPO_CategoryExt" + str(i) + ".Name") is not None:
            catextname = os.environ["NZBPO_CategoryExt" + str(i) + ".Name"];
            catextdestdir = os.environ["NZBPO_CategoryExt" + str(i) + ".DestDir"];
            catextaccess = os.environ["NZBPO_CategoryExt" + str(i) + ".Access"];
            catextowner = os.environ["NZBPO_CategoryExt" + str(i) + ".Owner"];
            catextgroup = os.environ["NZBPO_CategoryExt" + str(i) + ".Group"];

            if not re.match('^[0-7]{3}$', catextaccess):
                print(catextname,"Category: Invalid Access[mask]:",[catextaccess],CHECK_SETTINGS)
                check = SCRIPT_ERROR

            if not re.match('^[0-9]{1,}$', catextowner):
                print(catextname,"Category: Invalid Owner[UID]:",[catextowner],CHECK_SETTINGS)
                check = SCRIPT_ERROR
            else:
                try:
                    pwd.getpwuid(int(catextowner))
                except KeyError:
                    if overrideid == "yes":
                        print(catextname,"Category: Invalid Owner[UID]:",[catextowner],"User not in system.","<- ENABLED!!")
                    else:
                        print(catextname,"Category: Invalid Owner[UID]:",[catextowner],"User not in system.",CHECK_SETTINGS)
                        check = SCRIPT_ERROR

            if not re.match('^[0-9]{1,}$', catextgroup):
                print(catextname,"Category: Invalid Group[UID]:",[catextgroup],CHECK_SETTINGS)
                check = SCRIPT_ERROR
            else:
                try:
                    grp.getgrgid(int(catextgroup))
                except KeyError:
                    if overrideid == "yes":
                        print(catextname,"Category: Invalid Group[UID]:",[catextgroup],"Group not in system.","<- ENABLED!!")
                    else:
                        print(catextname,"Category: Invalid Group[UID]:",[catextgroup],"Group not in system.",CHECK_SETTINGS)
                        check = SCRIPT_ERROR

            for i in range(1, countcategory):
                if catextname == os.environ.get("NZBOP_Category" + str(i) + ".Name"):
                    if not catextdestdir == os.environ.get("NZBOP_Category" + str(i) + ".DestDir"):
                        print(catextname,"Category: Invalid Path:",[catextdestdir],CHECK_SETTINGS)
                        check = SCRIPT_ERROR

            catnames = []
            for i in range(1, countcategory):
                catname = os.environ.get("NZBOP_Category" + str(i) + ".Name")
                catnames.append(catname)
            if catextname not in catnames:
                print(catextname,"Category: Invalid CategoryExt Name:",[catextname],"Name not same as in CATEGORIES.",CHECK_SETTINGS)
                check = SCRIPT_ERROR

    try:
        check
    except NameError: 
        sys.exit(SCRIPT_SUCCESS)
    else:
        sys.exit(check)


# Add variables for added categories
categories = []
for i in range(1, 100):
    catextname = os.environ.get("NZBPO_CATEGORYEXT" + str(i) + "_NAME")
    catextdestdir = os.environ.get("NZBPO_CATEGORYEXT" + str(i) + "_DESTDIR")
    catextaccess = os.environ.get("NZBPO_CATEGORYEXT" + str(i) + "_ACCESS")
    catextowner = os.environ.get("NZBPO_CATEGORYEXT" + str(i) + "_OWNER")
    catextgroup = os.environ.get("NZBPO_CATEGORYEXT" + str(i) + "_GROUP")
    if catextname is None or catextdestdir is None:
        break
    categories.append({catextname, catextdestdir, catextaccess, catextowner, catextgroup})


# Init script options with values from NZBGet configuration file
category = os.environ['NZBPP_CATEGORY'];
nzbname = os.environ['NZBPP_NZBNAME'];
destdir = os.environ['NZBPO_DESTDIR'];
access = os.environ['NZBPO_ACCESS'];
owner = os.environ['NZBPO_OWNER'];
group = os.environ['NZBPO_GROUP'];


# If download is an added category, read in the related values and dir
if not category == "":
    for i in range(1, countcategoryext):
        if category == os.environ.get("NZBPO_CategoryExt" + str(i) + ".Name"):
            destdir = os.environ["NZBPO_CategoryExt" + str(i) + ".DestDir"];
            access = os.environ["NZBPO_CategoryExt" + str(i) + ".Access"];
            owner = os.environ["NZBPO_CategoryExt" + str(i) + ".Owner"];
            group = os.environ["NZBPO_CategoryExt" + str(i) + ".Group"];

# Check if input values are valid
if not re.match('^[0-7]{3}$', access):
    print(category,"Category: Invalid Access[mask]:",[access],CHECK_SETTINGS)
    sys.exit(SCRIPT_ERROR)

if not re.match('^[0-9]{1,}$', owner):
    print(category,"Category: Invalid Owner[UID]:",[owner],CHECK_SETTINGS)
    sys.exit(SCRIPT_ERROR)
else:
    try:
        pwd.getpwuid(int(owner))
    except KeyError:
        if overrideid == "yes":
            print(category,"Category: Invalid Owner[UID]:",[owner],"User not in system.","<- ENABLED!!")
        else:
            print(category,"Category: Invalid Owner[UID]:",[owner],"User not in system.",CHECK_SETTINGS)
            sys.exit(SCRIPT_ERROR)

if not re.match('^[0-9]{1,}$', group):
    print(category,"Category: Invalid Group[UID]:",[group],CHECK_SETTINGS)
    sys.exit(SCRIPT_ERROR)
else:
    try:
        grp.getgrgid(int(group))
    except KeyError:
        if overrideid == "yes":
            print(category,"Category: Invalid Group[UID]:",[group],"Group not in system.","<- ENABLED!!")
        else:
            print(category,"Category: Invalid Group[UID]:",[group],"Group not in system.",CHECK_SETTINGS)
            sys.exit(SCRIPT_ERROR)


# Apply chmod & chown to files in destination dir
if os.path.exists(os.path.join(destdir, nzbname)):
    print(category,": Modifying access permissions & ownership on",nzbname)
    os.chmod(os.path.join(destdir, nzbname), int(access, base=8))
    for root,dirs,files in os.walk(os.path.join(destdir, nzbname)):
        for d in dirs :
            os.chmod(os.path.join(root,d), int(access, base=8))
        for f in files :
            os.chmod(os.path.join(root,f), int(access, base=8))
    os.chown(os.path.join(destdir, nzbname), int(owner), int(group))
    for root,dirs,files in os.walk(os.path.join(destdir, nzbname)):
        for d in dirs :
            os.chown(os.path.join(root,d), int(owner), int(group))
        for f in files :
            os.chown(os.path.join(root,f), int(owner), int(group))

sys.exit(SCRIPT_SUCCESS)
