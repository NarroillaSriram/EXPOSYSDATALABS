// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CertificateRegistry {
    address public owner;

    struct Certificate {
        string certificateId;
        string studentName;
        string domainName;
        string issueDate;
        string certificateHash;
        string verificationUrl;
        bool isRevoked;
        bool exists;
    }

    mapping(string => Certificate) private certificates;

    event CertificateRegistered(
        string indexed certificateId,
        string studentName,
        string domainName,
        string issueDate,
        string certificateHash,
        string verificationUrl
    );

    event CertificateRevoked(string indexed certificateId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerCertificate(
        string memory _certificateId,
        string memory _studentName,
        string memory _domainName,
        string memory _issueDate,
        string memory _certificateHash,
        string memory _verificationUrl
    ) public onlyOwner {
        require(!certificates[_certificateId].exists, "Certificate already registered");
        certificates[_certificateId] = Certificate({
            certificateId: _certificateId,
            studentName: _studentName,
            domainName: _domainName,
            issueDate: _issueDate,
            certificateHash: _certificateHash,
            verificationUrl: _verificationUrl,
            isRevoked: false,
            exists: true
        });

        emit CertificateRegistered(
            _certificateId,
            _studentName,
            _domainName,
            _issueDate,
            _certificateHash,
            _verificationUrl
        );
    }

    function revokeCertificate(string memory _certificateId) public onlyOwner {
        require(certificates[_certificateId].exists, "Certificate does not exist");
        require(!certificates[_certificateId].isRevoked, "Certificate is already revoked");
        certificates[_certificateId].isRevoked = true;
        emit CertificateRevoked(_certificateId);
    }

    function getCertificate(string memory _certificateId)
        public
        view
        returns (
            string memory certificateId,
            string memory studentName,
            string memory domainName,
            string memory issueDate,
            string memory certificateHash,
            string memory verificationUrl,
            bool isRevoked,
            bool exists
        )
    {
        Certificate memory cert = certificates[_certificateId];
        return (
            cert.certificateId,
            cert.studentName,
            cert.domainName,
            cert.issueDate,
            cert.certificateHash,
            cert.verificationUrl,
            cert.isRevoked,
            cert.exists
        );
    }
}
