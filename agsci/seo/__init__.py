from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_module
from zope.i18nmessageid import MessageFactory
from DateTime import DateTime

seoMessageFactory = MessageFactory('agsci.seo')

allow_module('agsci.seo')

exclude_types = [
    'Cardinality Constraint',
    'Content Reference',
    'FSDCommittee',
    'FSDCommitteeMembership',
    'FSDCommitteesFolder',
    'FSDCourse',
    'FSDDepartment',
    'FSDDepartmentalMembership',
    'FSDFacultyStaffDirectoryTool',
    'FSDPersonGrouping',
    'FSDSpecialtiesFolder',
    'FSDSpecialty',
    'FSDSpecialtyInformation',
    'FieldsetEnd',
    'FieldsetFolder',
    'FieldsetStart',
    'FormBooleanField',
    'FormConfirmationPage',
    'FormMailerAdapter',
    'FormMultiSelectionField',
    'FormRichLabelField',
    'FormSaveDataAdapter',
    'FormSelectionField',
    'FormStringField',
    'FormTextField',
    'FormThanksPage',
    'Interface Constraint',
    'Inverse Implicator',
    'Link',
    'Newsletter',
    'Relations Library',
    'Ruleset Collection',
    'Ruleset',
    'TalkEvent',
    'Type Constraint',
]

def initialize(context):
    pass