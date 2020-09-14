import os
import enum


class StoreMode(enum.Enum):
    Copy = 0
    Zip = 1
    Encrypt = 2


class ConditionMode(enum.Enum):
    Always = 0
    IfUpdated = 1


class StoreItem(object):
    def __init__(self, item):
        if 'Path' in item:
            self.Path = item['Path']
        # TODO throw

        if 'Enabled' in item:
            self.Enabled = item['Enabled']
        else:
            self.Enabled = True

        if 'InnerPath' in item:
            self.InnerPath = item['InnerPath']
        else:
            self.InnerPath = os.path.basename(item['Path'])

        if 'Name' in item:
            self.Name = item['Name']
        else:
            self.Name = os.path.basename(item['Path'])

        if 'Mode' in item:
            self.Mode = StoreMode[item['Mode']]
        else:
            self.Mode = StoreMode.Zip

        if 'Condition' in item:
            self.Condition = ConditionMode[item['Condition']]
        else:
            self.Condition = 'Updated'
