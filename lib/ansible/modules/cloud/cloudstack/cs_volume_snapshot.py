#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2019, Gregor Riepl <onitake@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cs_volume_snapshot
short_description: Manages volume snapshots on Apache CloudStack clouds.
description:
    - Creates, lists, deletes and restores volume snapshots.
    - Snapshot sources can be volumes or VM snapshots.
version_added: '2.8'
author: Gregor Riepl (@onitake)
options:
  name:
    description:
      - The snapshot's name.
      - If not set, an automatically generated name is used.
    type: str
  volume:
    description:
      - Source volume
      - Required when creating a snapshot from a volume or VM snapshot.
    type: str
  vmsnapshot:
    description:
      - Source VM snapshot
      - Required when creating a snapshot from a VM snapshot.
    type: str
  state:
    description:
      - Present ensures the named snapshot exists, or creates it otherwise.
      - Absent removes the named snapshot.
      - Reverted reverts a volume to the named snapshot.
    type: str
    default: 'present'
    choices: [ 'present', 'absent', 'reverted' ]
  locationtype:
    description:
      - Specifies the destination storage for the snapshot.
      - Only supported for managed storage.
    type: str
    default: 'primary'
    choices: [ 'primary', 'secondary' ]
  policy:
    description:
      - Policy for automatic snapshots.
    type: str
    default: MANUAL_POLICY
  asyncbackup:
    description:
      - Create backups asynchronously.
    type: bool
    default: false
  quiescevm:
    description:
      - Quiesce VM before creating the snapshot.
    type: bool
    default: false
  domain:
    description:
      - Cloud domain that owns the volume or snapshot.
      - If not set, the default domain for the API key's account is used.
    type: str
  account:
    description:
      - Cloud account that owns the volume or snapshot.
      - If not set, the API key's account is used.
    type: str
  poll_async:
    description:
      - Poll async jobs until job has finished.
    type: bool
    default: yes
extends_documentation_fragment: cloudstack
'''

EXAMPLES = '''
- name: create volume snapshot
  cs_volume_snapshot:
    name: volume-1-snapshot-1
    volume: volume-1
  delegate_to: localhost

- name: create volume snapshot from VM snapshot
  cs_volume_snapshot:
    name: volume-1-snapshot-1
    volume: volume-1
    vmsnapshot: vm-1-snapshot-1
  delegate_to: localhost

- name: revert volume to snapshot
  cs_volume_snapshot:
    name: volume-1-snapshot-1
    state: reverted
  delegate_to: localhost

- name: delete volume snapshot
  cs_volume_snapshot:
    name: volume-1-snapshot-1
    state: absent
  delegate_to: localhost
'''

RETURN = '''
---
id:
  description: ID of the snapshot.
  returned: success
  type: str
  sample: ef9ce8df-a761-4897-97f6-6b895c088806
name:
  description: Name of the snapshot.
  returned: success
  type: str
  sample: volume-1-snapshot-1
created:
  description: Date when the snapshot was created.
  returned: success
  type: str
  sample: 2015-03-29T14:57:06+0200
state:
  description: State of the snapshot. Can be 'Creating', 'BackingUp' or 'BackedUp'.
  returned: success
  type: str
  sample: BackedUp
physicalsize:
  description: Effective size of the snapshot in bytes (?).
  returned: success
  type: int
  sample: 214521964
virtualsize:
  description: Effective size of the snapshot in bytes (?).
  returned: success
  type: int
  sample: 3281190722
locationtype:
  description: Where the snapshot is stored. 'primary' or 'secondary'.
  returned: success
  type: str
  sample: primary
snapshottype:
  description: Snapshot type (?).
  returned: success
  type: str
  sample: ?
intervaltype:
  description: Automatic snapshot period policy. 'hourly', 'daily', 'weekly', 'monthly', 'template' or 'none'.
  returned: success
  type: str
  sample: none
volumename:
  description: Name of the disk volume.
  returned: success
  type: str
  sample: volume-1
osdisplayname:
  description: Name of OS on volume.
  returned: success
  type: str
  sample: None
volumetype:
  description: Type of the disk volume.
  returned: success
  type: str
  sample: ?^
revertable:
  description: Whether reverting to the snapshot is supported.
  returned: success
  type: bool
  sample: true
domain:
  description: Cloud domain that owns the snapshot.
  returned: success
  type: str
  sample: example domain
account:
  description: Cloud account that owns the snapshot.
  returned: success
  type: str
  sample: example account
project:
  description: Name of project the snapshot is related to.
  returned: success
  type: str
  sample: Production
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_required_together,
    cs_argument_spec
)


class AnsibleCloudStackVolumeSnapshot(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackVolumeSnapshot, self).__init__(module)

    def create_snapshot(self):
        args = {
            'volumeid': self.get_volumeid(key='volume'),
            'name': self.get(key='name')
            'policyid': self.get_policyid(key='policy')
            'locationtype': self.get(key='locationtype')
            'quiescevm': self.get(key='quiescevm')
            'asyncbackup': self.get(key='asyncbackup')
        }

        if not self.module.check_mode:
            res = self.query_api('createSnapshot', **args)

            poll_async = self.module.params.get('poll_async')
            if res and poll_async:
                res = self.poll_job(res, 'snapshot')


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        name=dict(),
        volume=dict(),
        vmsnapshot=dict(),
        state=dict(),
            choices: [ 'present', 'absent', 'reverted' ]
        locationtype=dict(),
            choices: [ 'primary', 'secondary' ]
        policy=dict(),
        asyncbackup=dict(type='bool'),
        quiescevm=dict(type='bool'),
        domain=dict(),
        account=dict(),
        poll_async=dict(type='bool', default=True),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=cs_required_together(),
        supports_check_mode=True
    )

    acs_snapshot = AnsibleCloudStackVolumeSnapshot(module)
    state = self.get('state')
    if state == 'present':
        if self.get('vmsnapshot') is defined:
            acs_snapshot.create_vmsnapshot()
        else:
            acs_snapshot.create_snapshot()
    elif state == 'absent':
        acs_snapshot.delete_snapshot()
    elif state == 'reverted':
        acs_snapshot.revert_snapshot()
    result = acs_snapshot.get_result({'password': password})

    module.exit_json(**result)


if __name__ == '__main__':
    main()
