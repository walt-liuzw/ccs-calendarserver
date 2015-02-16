# -*- test-case-name: txdav.caldav.datastore.test.test_sql -*-
##
# Copyright (c) 2013-2015 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
"""
SQL backend for CalDAV storage when resources are external.
"""

from twisted.internet.defer import succeed, inlineCallbacks, returnValue

from twext.python.log import Logger

from txdav.caldav.datastore.sql import CalendarHome, Calendar, CalendarObject, \
    Attachment, AttachmentLink
from txdav.caldav.icalendarstore import ComponentUpdateState, ComponentRemoveState
from txdav.common.datastore.sql_external import CommonHomeExternal, CommonHomeChildExternal, \
    CommonObjectResourceExternal

log = Logger()

class CalendarHomeExternal(CommonHomeExternal, CalendarHome):
    """
    Wrapper for a CalendarHome that is external and only supports a limited set of operations.
    """

    def __init__(self, transaction, ownerUID, resourceID):

        CalendarHome.__init__(self, transaction, ownerUID)
        CommonHomeExternal.__init__(self, transaction, ownerUID, resourceID)


    def hasCalendarResourceUIDSomewhereElse(self, uid, ok_object, mode):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def getCalendarResourcesForUID(self, uid):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def calendarObjectWithDropboxID(self, dropboxID):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    @inlineCallbacks
    def getAllAttachments(self):
        """
        Return all the L{Attachment} objects associated with this calendar home.
        Needed during migration.
        """
        raw_results = yield self._txn.store().conduit.send_home_get_all_attachments(self)
        returnValue([Attachment.deserialize(self._txn, attachment) for attachment in raw_results])


    @inlineCallbacks
    def readAttachmentData(self, remote_id, attachment):
        """
        Read the data associated with an attachment associated with this calendar home.
        Needed during migration only.
        """
        stream = attachment.store(attachment.contentType(), attachment.name(), migrating=True)
        yield self._txn.store().conduit.send_get_attachment_data(self, remote_id, stream)


    @inlineCallbacks
    def getAttachmentLinks(self):
        """
        Read the attachment<->calendar object mapping data associated with this calendar home.
        Needed during migration only.
        """
        raw_results = yield self._txn.store().conduit.send_home_get_attachment_links(self)
        returnValue([AttachmentLink.deserialize(self._txn, attachment) for attachment in raw_results])


    def getAllDropboxIDs(self):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def getAllAttachmentNames(self):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def getAllManagedIDs(self):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def createdHome(self):
        """
        No children - make this a no-op.
        """
        return succeed(None)


    def splitCalendars(self):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def ensureDefaultCalendarsExist(self):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def setDefaultCalendar(self, calendar, componentType):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def defaultCalendar(self, componentType, create=True):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def isDefaultCalendar(self, calendar):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def getDefaultAlarm(self, vevent, timed):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def setDefaultAlarm(self, alarm, vevent, timed):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def getAvailability(self):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")


    def setAvailability(self, availability):
        """
        No children.
        """
        raise AssertionError("CommonHomeExternal: not supported")



class CalendarExternal(CommonHomeChildExternal, Calendar):
    """
    SQL-based implementation of L{ICalendar}.
    """
    pass



class CalendarObjectExternal(CommonObjectResourceExternal, CalendarObject):
    """
    SQL-based implementation of L{ICalendarObject}.
    """

    @classmethod
    def _createInternal(cls, parent, name, component, internal_state, options=None, split_details=None):
        raise AssertionError("CalendarObjectExternal: not supported")


    def _setComponentInternal(self, component, inserting=False, internal_state=ComponentUpdateState.NORMAL, options=None, split_details=None):
        raise AssertionError("CalendarObjectExternal: not supported")


    def _removeInternal(self, internal_state=ComponentRemoveState.NORMAL):
        raise AssertionError("CalendarObjectExternal: not supported")


    @inlineCallbacks
    def addAttachment(self, rids, content_type, filename, stream):
        result = yield self._txn.store().conduit.send_add_attachment(self, rids, content_type, filename, stream)
        managedID, location = result
        returnValue((ManagedAttachmentExternal(str(managedID)), str(location),))


    @inlineCallbacks
    def updateAttachment(self, managed_id, content_type, filename, stream):
        result = yield self._txn.store().conduit.send_update_attachment(self, managed_id, content_type, filename, stream)
        managedID, location = result
        returnValue((ManagedAttachmentExternal(str(managedID)), str(location),))


    @inlineCallbacks
    def removeAttachment(self, rids, managed_id):
        yield self._txn.store().conduit.send_remove_attachment(self, rids, managed_id)
        returnValue(None)



class ManagedAttachmentExternal(object):
    """
    Fake managed attachment object returned from L{CalendarObjectExternal.addAttachment} and
    L{CalendarObjectExternal.updateAttachment}.
    """

    def __init__(self, managedID):
        self._managedID = managedID


    def managedID(self):
        return self._managedID


CalendarExternal._objectResourceClass = CalendarObjectExternal
