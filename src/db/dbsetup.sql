create table if not exists `company` (
    id int not null auto_increment,
    company_name varchar(100) not null,
    bank_name varchar(100) not null,
    account_number varchar(100) not null,
    ifsc_code varchar(100) not null,
    primary key (id)
) ENGINE=InnoDB;

CREATE TABLE `employees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_number` varchar(10) NOT NULL,
  `password` varchar(100) not null,
  `employee_name` varchar(100) NOT NULL,
  `employee_email` varchar(100)NOT NULL,
  `bank_name` varchar(100) NOT NULL,
  `account_number` varchar(100) NOT NULL,
  `ifsc_code` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_number_UNIQUE` (`employee_number`)
) ENGINE=InnoDB;

create table `roles` (
  `employee_number` varchar(10) not null,
  `role` varchar(20) not null,
  CONSTRAINT `fk_emp_role` FOREIGN KEY (`employee_number`) 
    REFERENCES `employees` (`employee_number`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `expense_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_number` varchar(10) NOT NULL,
  `create_ts` timestamp not null,
  `last_update_ts` timestamp not null,
  `title` varchar(100) not null,
  `status` varchar(50) NOT NULL,
  `approver_employee_number` varchar(10),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_emp_report_emp` FOREIGN KEY (`employee_number`) 
    REFERENCES `employees` (`employee_number`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

create table `expense_report_approval_queue` (
  `report_id` int not null,
  `approver_employee_number` varchar(10) not null,
  CONSTRAINT `fk_emp_report_id` FOREIGN KEY (`report_id`) 
    REFERENCES `expense_reports` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_emp_report_approver` FOREIGN KEY (`approver_employee_number`) 
    REFERENCES `employees` (`employee_number`) ON DELETE CASCADE ON UPDATE CASCADE
);

create table `expense_types` (
  `type` varchar(100) not null,
  primary key(type)
);

create table `currencies` (
  `ccy` varchar(20) not null,
  `ccy_name` varchar(100) not null,
  `country_name` varchar(200) not null,
  primary key(ccy)
);

create table `expenses` (
    `id` int NOT NULL AUTO_INCREMENT,
    `expense_report_id` int not null,
    `type` varchar(100) not null,
    `create_ts` timestamp not null,
    `location` varchar(100) not null,
    `amount` decimal(20,2) not null,
    `currency` varchar(20) not null,
    `purpose` varchar(100) not null,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_exp_expr_report` FOREIGN KEY (`expense_report_id`) 
      REFERENCES `expense_reports` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_exp_expense_type` FOREIGN KEY (`type`) 
      REFERENCES `expense_types` (`type`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_exp_currency` FOREIGN KEY (`currency`) 
      REFERENCES `currencies` (`ccy`) ON DELETE CASCADE ON UPDATE CASCADE
);
