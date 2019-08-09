# This helper script downloads the Greengrass Group CA certificate
import boto3

gg = boto3.client('greengrass')

# Obtain the group id from the AWS Management Console, go to Greengrass, select the group and go to settings
GROUP_ID = '<YOUR_GREENGRASS_GROUP_ID>'

ca = gg.list_group_certificate_authorities(GroupId = GROUP_ID)['GroupCertificateAuthorities'][0]

cert = gg.get_group_certificate_authority(CertificateAuthorityId = ca['GroupCertificateAuthorityId'], GroupId = GROUP_ID)['PemEncodedCertificate']

with open('certs/rootca.pem', 'w') as f:
    f.write(cert)