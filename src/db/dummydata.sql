delete from expense_reports;
delete from employees;

insert into employees ( `employee_number`, 
                        `password`, 
                        `employee_name`, 
                        `employee_email`,
                        `bank_name`, 
                        `account_number`, 
                        `ifsc_code`)
values('1', '1234', 'Tanisha Bhide', 'tanisha.demo@gmail.com', 'Deutsche Bank', '12345678', 'DEUTINPBC');

commit;

insert into expense_reports (
        `employee_number`,
        `create_ts`,
        `last_update_ts`,
        `title`,
        `status`
        )
 values ('1', utc_timestamp(), utc_timestamp(), 'Customer event in Bangalore', 'DRAFT');

insert into expense_reports (
        `employee_number`,
        `create_ts`,
        `last_update_ts`,
        `title`,
        `status`
        )
 values ('1', utc_timestamp(), utc_timestamp(), 'Travel to Germany', 'REIMBURSED');

insert into expense_reports (
        `employee_number`,
        `create_ts`,
        `last_update_ts`,
        `title`,
        `status`
        )
 values ('1', utc_timestamp(), utc_timestamp(), 'Hardware purchase', 'REJECTED');
  