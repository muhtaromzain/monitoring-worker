DROP TABLE `customer_portal_temp`;
CREATE TABLE `customer_portal_temp` (
	`dt_code` VARCHAR(100) COLLATE utf8mb4_unicode_ci NOT NULL,
	`order_number` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
	`sku` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
	`qty` INT(11) UNSIGNED DEFAULT 0,
	`created_on` INT(11) UNSIGNED NOT NULL
);

DROP TABLE `customer_portal_headers`;
CREATE TABLE `customer_portal_headers` (
	`dt_code` VARCHAR(100) COLLATE utf8mb4_unicode_ci NOT NULL,
	`order_number` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
	`customer_code` VARCHAR(10) NULL,
	`warehouse_code` VARCHAR(10) NULL,
	`term_code` VARCHAR(4) NULL,
	`is_submitted` TINYINT(1) DEFAULT 0,
	`remarks` LONGTEXT NULL,
	`send_timestamps` INT(11) UNSIGNED DEFAULT NULL,
	`created_on` INT(11) UNSIGNED NOT NULL,
	UNIQUE KEY `uk_customer_portal_header_dt_code_created_on` (`dt_code`, `created_on`) USING BTREE,
	INDEX `ix_customer_portal_headers_dt_code` (`dt_code`) USING BTREE,
	INDEX `ix_customer_portal_headers_order_number` (`order_number`) USING BTREE,
	INDEX `ix_customer_portal_headers_created_on` (`created_on`) USING BTREE
);

DROP TABLE `customer_portal`;
CREATE TABLE `customer_portal` (
	`dt_code` VARCHAR(100) COLLATE utf8mb4_unicode_ci NOT NULL,
	`order_number` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
	`sku` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
	`qty` INT(11) UNSIGNED DEFAULT 0,
	`created_on` INT(11) UNSIGNED NOT NULL,
	INDEX `ix_customer_portal_dt_code` (`dt_code`) USING BTREE,
	INDEX `ix_customer_portal_order_number` (`order_number`) USING BTREE,
	INDEX `ix_customer_portal_created_on` (`created_on`) USING BTREE,
	CONSTRAINT `fk_customer_portal_dt_code_created_on_idx` FOREIGN KEY (`dt_code`, `created_on`) REFERENCES `customer_portal_headers` (`dt_code`, `created_on`) ON DELETE CASCADE ON UPDATE NO ACTION
);