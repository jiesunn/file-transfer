CREATE TABLE file_transfer.power (
	`id` TINYINT DEFAULT 1 NOT NULL,
	`info` varchar(10) DEFAULT 'user' NOT NULL COMMENT '权限'
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci
COMMENT='权限表';

CREATE TABLE file_transfer.users (
	`id` INT unsigned NOT NULL auto_increment,
	`pid` TINYINT DEFAULT 1 NOT NULL COMMENT '权限',
	`sub` varchar(10) DEFAULT '' NOT NULL COMMENT '描述（用户名）',
	`pwd` varchar(50) DEFAULT '' NOT NULL COMMENT '密码',
	`phone` varchar(20) DEFAULT '' NOT NULL COMMENT '手机号',
	`email` varchar(50) DEFAULT '' NOT NULL COMMENT '邮箱',
	`intro` varchar(100) DEFAULT '' NOT NULL COMMENT '自我介绍',
	`create_time` DATETIME COMMENT '创建时间',
    PRIMARY KEY (`id`),
	UNIQUE KEY (`sub`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci
COMMENT='用户表';

CREATE TABLE file_transfer.logs (
	`id` INT unsigned NOT NULL auto_increment,
	`level` varchar(10) DEFAULT '' NOT NULL COMMENT '日志等级',
	`method` varchar(10) DEFAULT '' NOT NULL COMMENT '请求类型',
	`path` varchar(50) DEFAULT '' NOT NULL COMMENT '请求地址',
	`params` varchar(100) DEFAULT '' NOT NULL COMMENT '请求参数',
	`response` varchar(200) DEFAULT '' NOT NULL COMMENT '返回内容',
	`user_ip` varchar(50) DEFAULT '' NOT NULL COMMENT '用户IP',
	`request_time` DATETIME COMMENT '请求时间',
    PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci
COMMENT='日志表';
