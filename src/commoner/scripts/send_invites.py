"""
This module is used to fetch the individuals who have made donations
at support.cc.org that are large enough to grant them account at
CC Network. If the donor has contributed above a specific amount, then
a promo code will be generated for them and sent to the email address
they used at donation time.
"""

import warnings
import sys
import sqlalchemy
import datetime 

from commoner.promocodes.models import PromoCode

PRODUCTION = False
warnings.simplefilter("ignore", UserWarning)

def main():
    
    start_date = "2009-09-15"

    # setup database connectivity
    if PRODUCTION:
        db = sqlalchemy.create_engine('mysql://civicrm:Civicrm.@localhost/civicrm', convert_unicode=True, encoding='latin1') 
    else:
        db = sqlalchemy.create_engine('mysql://civicrm:Civicrm.@localhost/civicrm_staging', convert_unicode=True, encoding='latin1')

    metadata = sqlalchemy.MetaData(db)
    tbl_contrib = sqlalchemy.Table('civicrm_contribution', metadata, autoload=True)
    tbl_recur = sqlalchemy.Table('civicrm_contribution_recur', metadata, autoload=True)
    tbl_contact = sqlalchemy.Table('civicrm_contact', metadata, autoload=True)
    if PRODUCTION:
        tbl_paypal = sqlalchemy.Table('civicrm_value_1_paypal_data_7', metadata, autoload=True)
    else:
        tbl_paypal = sqlalchemy.Table('civicrm_value_1_paypal_data_7', metadata, autoload=True)

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
            receive_date >= start_date, 
            receipt_date.like(str(datetime.date.today()) + '%'), 
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
            email = tbl_email.select(email_id == contrib['contact_id']).execute().fetchone()

            # We may utilize this again in the future...
            # paypal = tbl_paypal.select(tbl_paypal.c.entity_id == contrib['contact_id']).execute().fetchone()

            # make that promo code has not been created for this contribution
            if PromoCode.objects.filter(contribution_id = contrib['invoice_id']).count() == 0:
                # send the welcome
                if email:
                    p = PromoCode.objects.create_promo_code(
                            unicode(email['email']), # email addr
                            unicode(contrib['trxn_id']), # paypal transaction id
                            unicode(contrib['invoice_id']),
                            PRODUCTION)  # civicrm contribution id

                    print "%s, %s" % (p.code, p.recipient)

if __name__ == '__main__':
    main()
