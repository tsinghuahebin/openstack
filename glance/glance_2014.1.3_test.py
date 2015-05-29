from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
from glanceclient import Client
import uuid

AUTH_URL = "http://166.111.67.30:5000/v2.0"
USERNAME = "demo"
PASSWORD = "639b8d5a7618482f"
PROJECT_ID = "demo"
OS_IMAGE_ENDPOINT = "http://166.111.67.30:9292"
file_location = "http://archive.ubuntu.com/ubuntu/dists/precise-updates/main/installer-amd64/current/images/trusty-netboot/mini.iso"

auth = identity.Password(auth_url=AUTH_URL,
                         username=USERNAME,
                         password=PASSWORD,
                         tenant_name=PROJECT_ID)

sess = session.Session(auth=auth)
token = auth.get_token(sess)
glance = Client('1', endpoint=OS_IMAGE_ENDPOINT, token=token)
id = str(uuid.uuid4())
image = glance.images.create(name=id,
                            copy_from=file_location,
                            is_public=True,
                            disk_format='ami')

image = glance.images.get(image.id)
if image.status == "saving":
    print("Image status = = %s" % image.status)
    glance.images.delete(image)
    print("Image %s deleted in saving state" % image.id)
else:
    print ("The image is in %s status, Not in saving. Run script again!" % image.status)