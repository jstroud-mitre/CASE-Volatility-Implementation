# 'Approved for Public Release; Distribution Unlimited. Case Number 18-0922'.

# NOTICE
# 
# This software was produced for the U.S. Government under
# contract SB-1341-14-CQ-0010, and is subject to the Rights
# in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
#
# (c) 2018 The MITRE Corporation. All Rights Reserved.


# Volatility
# Copyright (C) 2007-2013 Volatility Foundation
#
# Additional Authors:
# Michael Ligh <michael.ligh@mnin.org>
#
# This file is part of Volatility.
#
# Volatility is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Volatility is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Volatility.  If not, see <http://www.gnu.org/licenses/>.
#


try:
    import sys
    import getpass
    import datetime
    from volatility import renderers
    from volatility.renderers.basic import Address, Hex
    import volatility.plugins.taskmods as taskmods
    import case
except ImportError as err:
    print("[Error] %s")
    sys.exit()

class CASEHandles(taskmods.DllList):
    '''
    Windows process list presented in CASE format.
    '''


    def __init__(self, config, *args, **kwargs):

        # CASE Specific structure to create CASE Document.
        self.document = case.Document()
        self.instrument = self.document.create_uco_object(
            'Tool',
            name='Volatility',
            version='2.6',
            toolType="Forensics"
        )
        self.performer = self.document.create_uco_object('Identity', uri=getpass.getuser())
        self.performer.create_property_bundle('Username: ',
           Name=getpass.getuser())

        self.action = self.document.create_uco_object('InvestigativeAction',
                                                      startTime=datetime.datetime.now().isoformat(),
                                                      endTime=datetime.datetime.now().isoformat())

        taskmods.DllList.__init__(self, config, *args, **kwargs)
        config.add_option("PHYSICAL-OFFSET", short_option = 'P', default = False,
                          help = "Physical Offset", action = "store_true")
        config.add_option("OBJECT-TYPE", short_option = 't', default = None,
                          help = 'Show these object types (comma-separated)',
                          action = 'store', type = 'str')
        config.add_option("SILENT", short_option = 's', default = False,
                          action = 'store_true', help = 'Suppress less meaningful results')



    def generator(self, data):
        if self._config.OBJECT_TYPE:
            object_list = [s.lower() for s in self._config.OBJECT_TYPE.split(',')]
        else:
            object_list = []
        for pid, handle, object_type, name in data:
            if object_list and object_type.lower() not in object_list:
                continue
            if self._config.SILENT:
                if len(name.replace("'", "")) == 0:
                    continue
            if not self._config.PHYSICAL_OFFSET:
                offset = handle.Body.obj_offset
            else:
                offset = handle.obj_vm.vtop(handle.Body.obj_offset)

            yield (0, [Address(offset),
                          int(pid),
                          Hex(handle.HandleValue),
                          Hex(handle.GrantedAccess),
                          str(object_type),
                          str(name)])

    def unified_output(self, data):
        offsettype = "(V)" if not self._config.PHYSICAL_OFFSET else "(P)"
        tg = renderers.TreeGrid(
                          [("Offset{0}".format(offsettype), Address),
                           ("Pid", int),
                           ("Handle", Hex),
                           ("Access", Hex),
                           ("Type", str),
                           ("Details", str),
                           ], self.generator(data))
        return tg

    def render_text(self, outfd, data):
        offsettype = "(V)" if not self._config.PHYSICAL_OFFSET else "(P)"

        self.table_header(outfd,
                          [("Offset{0}".format(offsettype), "[addrpad]"),
                           ("Pid", ">6"),
                           ("Handle", "[addr]"),
                           ("Access", "[addr]"),
                           ("Type", "16"),
                           ("Details", "")
                           ])

        if self._config.OBJECT_TYPE:
            object_list = [s.lower() for s in self._config.OBJECT_TYPE.split(',')]
        else:
            object_list = []

        for pid, handle, object_type, name in data:
            if object_list and object_type.lower() not in object_list:
                continue
            if self._config.SILENT:
                if len(name.replace("'", "")) == 0:
                    continue
            if not self._config.PHYSICAL_OFFSET:
                offset = handle.Body.obj_offset
            else:
                offset = handle.obj_vm.vtop(handle.Body.obj_offset)

            ### CASE structure from data extracted.
            self.action.create_property_bundle(
                'ActionReferences',
                performer=self.performer,
                instrument=self.instrument,
                ProcessID=pid,
                ProcessName=name,
                HandleID=handle.HandleValue,
                Handle=handle.GrantedAccess,
                Object=object_type
            )
            print(self.document.serialize(format="json-ld", destination=None))

    def calculate(self):
        for task in taskmods.DllList.calculate(self):
            pid = task.UniqueProcessId
            if task.ObjectTable.HandleTableList:
                for handle in task.ObjectTable.handles():

                    if not handle.is_valid():
                        continue

                    name = ""
                    object_type = handle.get_object_type()
                    if object_type == "File":
                        file_obj = handle.dereference_as("_FILE_OBJECT")
                        name = str(file_obj.file_name_with_device())
                    elif object_type == "Key":
                        key_obj = handle.dereference_as("_CM_KEY_BODY")
                        name = key_obj.full_key_name()
                    elif object_type == "Process":
                        proc_obj = handle.dereference_as("_EPROCESS")
                        name = "{0}({1})".format(proc_obj.ImageFileName, proc_obj.UniqueProcessId)
                    elif object_type == "Thread":
                        thrd_obj = handle.dereference_as("_ETHREAD")
                        name = "TID {0} PID {1}".format(thrd_obj.Cid.UniqueThread, thrd_obj.Cid.UniqueProcess)
                    elif handle.NameInfo.Name == None:
                        name = ''
                    else:
                        name = str(handle.NameInfo.Name)

                    yield pid, handle, object_type, name