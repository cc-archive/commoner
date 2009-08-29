"""
This module is used to fetch the individuals who have made donations
at support.cc.org that are large enough to grant them account at
CC Network. If the donor has contributed above a specific amount, then
a promo code will be generated for them and sent to the email address
they used at donation time.
"""

import warnings
warnings.simplefilter("ignore", UserWarning)

import sys
import os
import sqlalchemy
import datetime 

os.environ['DJANGO_SETTINGS_MODULE'] = 'commoner.settings'

from commoner.premium.models import PromoCode

PRODUCTION = True

if len(sys.argv) > 1:
    date = sys.argv[-1]
else:
    date = str(datetime.date.today()) #sys.argv[1]

# setup database connectivity
db = sqlalchemy.create_engine('mysql://root@localhost/civicrm_staging', convert_unicode=True, encoding='latin1')
if PRODUCTION:
    db = sqlalchemy.create_engine('mysql://civicrm:Civicrm.@localhost/civicrm', convert_unicode=True, encoding='latin1') 
metadata = sqlalchemy.MetaData(db)
tbl_contrib = sqlalchemy.Table('civicrm_contribution', metadata, autoload=True)
tbl_recur = sqlalchemy.Table('civicrm_contribution_recur', metadata, autoload=True)
tbl_contact = sqlalchemy.Table('civicrm_contact', metadata, autoload=True)
if PRODUCTION:
    tbl_paypal = sqlalchemy.Table('civicrm_value_1_paypal_data_7', metadata, autoload=True)
else:
    tbl_paypal = sqlalchemy.Table('civicrm_value_1_paypal_data_8', metadata, autoload=True)

tbl_email = sqlalchemy.Table('civicrm_email', metadata, autoload=True)

# Fetch some of the column objects we'll need
recur_id = tbl_recur.c.id
contact_id = tbl_contact.c.id
email_id = tbl_email.c.contact_id
paypal_id = tbl_paypal.c.entity_id
receive_date = tbl_contrib.c.receive_date
receipt_date = tbl_contrib.c.receipt_date
status_id = tbl_contrib.c.contribution_status_id
contrib_type_id = tbl_contrib.c.contribution_type_id

# Select all completed contributions that were started on or before the 
# campaign launch date, and which were completed on the date provided.
contribs = tbl_contrib.select(
    sqlalchemy.and_(
        receive_date >= '2009-09-15', 
	receipt_date.like(date + '%'), 
	status_id == 1)
    ).execute().fetchall()

for contrib in contribs:
    is_student = False
    is_recurring = False

    transaction_id = contrib['trxn_id']

    # If the field contribution_page_id is 16 (student) then they are
    # automatically a member, else we check if this is a recurring contribution
    # and if it is we calculate the total contribution, else we just look at
    # the field total_amount of the contribution.  If these latter 2 are
    # greater than 50 then they qualify to be a member
    if contrib['contribution_page_id'] == 16:
        # This is a student
	is_student = True

    if contrib['contribution_recur_id']:
        is_recurring = True
        transaction_id = str(contrib['contribution_recur_id'])

        # This is a recurring contribution, calculate the total contribution.
        recur = tbl_recur.select(recur_id == contrib['contribution_recur_id']).execute().fetchone()

        ttl_contrib = recur['amount']

	#if recur['installments']:
        #    ttl_contrib = recur['amount'] * recur['installments']
	#else:
	#    print "Recurring donation (%s) for %s with no installments" % (recur['amount'], transaction_id)

    else:
        ttl_contrib = contrib['total_amount']

    # If the total is more than 50, then they qualify to be a member
    is_member = False

    if is_student:
        if ttl_contrib >= 25:
            is_member = True
    elif is_recurring:
        if ttl_contrib >= 8.33:
	    is_member = True
    elif contrib['contribution_type_id'] == 6:
        if ttl_contrib >= 100:
            is_member = True
    elif ttl_contrib >= 50:
        is_member = True

    if is_member:
        contact = tbl_contact.select(contact_id == contrib['contact_id']).execute().fetchone()
        paypal = tbl_paypal.select(tbl_paypal.c.entity_id == contrib['contact_id']).execute().fetchone()
        email = tbl_email.select(email_id == contrib['contact_id']).execute().fetchone()

        if paypal:
            pp_fname = paypal['first_name']
            pp_lname = paypal['last_name']
        else:
            pp_fname = contact['first_name']
            pp_lname = contact['last_name']

    # see if this has been processed
	if PromoCode.objects.filter(transaction_id = transaction_id).count() > 0 ||
       PromoCode.objects.filter(contribution_id = contrib['id']).count() > 0:
	    continue

    # send the welcome
	PromoCode.objects.create_registration(
	    unicode(transaction_id),
	    unicode(email['email']), unicode(pp_lname), unicode(pp_fname))

        member = []
        member.append(pp_fname)
        member.append(pp_lname)
        member.append(transaction_id)
        member.append(email['email'])

        print ','.join([field for field in member])
