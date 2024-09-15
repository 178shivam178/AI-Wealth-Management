CREATE DATABASE AI_Wealth;

USE AI_Wealth;

CREATE TABLE Personal_Info (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    BankName VARCHAR(255) NOT NULL,
    PersonName VARCHAR(255) NOT NULL,
    BranchName VARCHAR(255) NOT NULL,
    PersonAddress VARCHAR(255),
    BankAddress VARCHAR(255),
    AccountNo VARCHAR(20) UNIQUE NOT NULL,
    IFSC VARCHAR(11) NOT NULL,
    CustomerID VARCHAR(20) UNIQUE NOT NULL,
    INDEX (BankName, PersonName, AccountNo)
);

CREATE TABLE Transaction_Info (
    ID INT,
    BankName VARCHAR(255),
    PersonName VARCHAR(255),
    AccountNo VARCHAR(20),
    TransactionDate DATE,
    ValueDate DATE,
    Description VARCHAR(255),
    Debit DECIMAL(15, 2),
    Credit DECIMAL(15, 2),
    Balance DECIMAL(15, 2),
    label VARCHAR(20),
    FOREIGN KEY (ID) REFERENCES Personal_Info(ID),
    FOREIGN KEY (BankName, PersonName, AccountNo) 
        REFERENCES Personal_Info(BankName, PersonName, AccountNo)
);
