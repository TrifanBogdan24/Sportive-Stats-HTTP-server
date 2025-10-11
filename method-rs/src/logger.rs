pub enum LogType {
    Info,
    Error
}


use chrono::{DateTime, Utc};

const TIME_FORMAT: &str = "%Y-%m-%d %H:%M:%S";


pub fn print_log(log_type: LogType, msg: &str) {
    let time_now: DateTime<Utc> = Utc::now();
    let fmt_time = time_now.format(TIME_FORMAT).to_string();

    match log_type {
        LogType::Info => println!("{:} - INFO - {:}", fmt_time, msg),
        LogType::Error => println!("{:} - ERROR - {:}", fmt_time, msg),
    }
}

