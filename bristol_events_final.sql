-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: bristol_events_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary view structure for view `available_slots`
--

DROP TABLE IF EXISTS `available_slots`;
/*!50001 DROP VIEW IF EXISTS `available_slots`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `available_slots` AS SELECT 
 1 AS `Event_ID`,
 1 AS `Title`,
 1 AS `Total_Capacity`,
 1 AS `Slots_Sold`,
 1 AS `Slots_Left`,
 1 AS `If_Sold_Out`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `booking_days`
--

DROP TABLE IF EXISTS `booking_days`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_days` (
  `Booking_ID` int NOT NULL,
  `Day_ID` int NOT NULL,
  PRIMARY KEY (`Booking_ID`,`Day_ID`),
  KEY `Day_ID` (`Day_ID`),
  CONSTRAINT `booking_days_ibfk_1` FOREIGN KEY (`Booking_ID`) REFERENCES `bookings` (`Booking_ID`) ON DELETE CASCADE,
  CONSTRAINT `booking_days_ibfk_2` FOREIGN KEY (`Day_ID`) REFERENCES `event_days` (`Day_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_days`
--

LOCK TABLES `booking_days` WRITE;
/*!40000 ALTER TABLE `booking_days` DISABLE KEYS */;
INSERT INTO `booking_days` VALUES (12,65),(2,66),(10,67),(14,67),(15,67),(4,78),(5,78),(6,79),(7,79),(11,82),(13,82);
/*!40000 ALTER TABLE `booking_days` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `Booking_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Event_ID` int NOT NULL,
  `Booking_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `Tickets_Purchased` int NOT NULL,
  `Ticket_Price` decimal(10,2) NOT NULL,
  `Booking_Status` enum('Success','Cancelled','Pending') DEFAULT 'Pending',
  `Original_Price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `Discount_Applied` decimal(10,2) NOT NULL DEFAULT '0.00',
  `Is_Student` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`Booking_ID`),
  KEY `User_ID` (`User_ID`),
  KEY `Event_ID` (`Event_ID`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`Event_ID`) REFERENCES `events` (`Event_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1,2,1,'2026-04-23 22:41:50',1,18.00,'Success',20.00,2.00,1),(2,2,1,'2026-04-23 22:43:28',1,20.00,'Success',20.00,0.00,0),(4,1,17,'2026-04-24 15:56:21',10,150.00,'Success',150.00,0.00,0),(5,1,17,'2026-04-24 15:57:38',10,150.00,'Cancelled',150.00,0.00,0),(6,1,18,'2026-04-24 16:28:29',7,33.25,'Cancelled',35.00,1.75,0),(7,1,18,'2026-04-24 16:28:43',3,12.75,'Cancelled',15.00,2.25,1),(8,1,3,'2026-04-24 17:39:46',1,27.00,'Success',30.00,3.00,1),(10,2,1,'2026-04-24 18:44:24',1,18.00,'Success',20.00,2.00,1),(11,2,3,'2026-04-24 18:49:58',1,30.00,'Success',30.00,0.00,0),(12,2,15,'2026-04-24 19:55:04',1,45.00,'Success',50.00,5.00,0),(13,1,3,'2026-04-24 20:28:08',1,27.00,'Success',30.00,3.00,1),(14,1,1,'2026-04-24 20:45:54',1,18.00,'Success',20.00,2.00,1),(15,2,1,'2026-04-24 20:54:27',1,18.00,'Success',20.00,2.00,1);
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `Category_ID` int NOT NULL AUTO_INCREMENT,
  `Category_name` varchar(50) NOT NULL,
  PRIMARY KEY (`Category_ID`),
  UNIQUE KEY `Category_name` (`Category_name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (4,'Art'),(8,'Comedy'),(10,'Family'),(7,'Food & Drink'),(1,'Music'),(6,'Nightlife'),(5,'Science'),(3,'Sports'),(2,'Theatre'),(9,'Workshops');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `event_cards`
--

DROP TABLE IF EXISTS `event_cards`;
/*!50001 DROP VIEW IF EXISTS `event_cards`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `event_cards` AS SELECT 
 1 AS `event_id`,
 1 AS `title`,
 1 AS `desc`,
 1 AS `date`,
 1 AS `end_date`,
 1 AS `venue`,
 1 AS `category`,
 1 AS `price`,
 1 AS `image`,
 1 AS `capacity`,
 1 AS `available_slots`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `event_days`
--

DROP TABLE IF EXISTS `event_days`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_days` (
  `Day_ID` int NOT NULL AUTO_INCREMENT,
  `Event_ID` int NOT NULL,
  `Date` date NOT NULL,
  `Start_Time` time NOT NULL,
  `End_Time` time NOT NULL,
  `Day_Capacity` int NOT NULL,
  PRIMARY KEY (`Day_ID`),
  KEY `Event_ID` (`Event_ID`),
  CONSTRAINT `event_days_ibfk_1` FOREIGN KEY (`Event_ID`) REFERENCES `events` (`Event_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_days`
--

LOCK TABLES `event_days` WRITE;
/*!40000 ALTER TABLE `event_days` DISABLE KEYS */;
INSERT INTO `event_days` VALUES (4,4,'2025-06-12','10:00:00','18:00:00',500),(5,4,'2025-06-13','10:00:00','18:00:00',500),(6,5,'2025-07-01','22:00:00','04:00:00',1500),(7,6,'2025-07-05','19:30:00','22:30:00',550),(27,8,'2026-04-17','03:10:00','13:00:00',500),(28,8,'2026-04-18','03:10:00','13:00:00',500),(38,7,'2026-04-18','04:00:00','08:00:00',350),(39,7,'2026-04-19','04:00:00','08:00:00',350),(55,11,'2026-06-20','10:00:00','22:00:00',500),(65,15,'2026-05-22','15:30:00','20:00:00',50),(66,1,'2026-04-23','22:50:00','23:59:00',2000),(67,1,'2026-04-24','22:50:00','23:59:00',2000),(68,1,'2026-04-25','22:50:00','23:59:00',2000),(69,1,'2026-04-26','22:50:00','23:59:00',2000),(70,1,'2026-04-27','22:50:00','23:59:00',2000),(71,1,'2026-04-28','22:50:00','23:59:00',2000),(72,1,'2026-04-29','22:50:00','23:59:00',2000),(73,1,'2026-04-30','22:50:00','23:59:00',2000),(74,1,'2026-05-01','22:50:00','23:59:00',2000),(75,1,'2026-05-02','22:50:00','23:59:00',2000),(78,17,'2026-05-02','13:30:00','17:00:00',20),(79,18,'2026-05-13','08:30:00','13:30:00',10),(81,13,'2026-06-06','13:00:00','17:30:00',100),(82,3,'2026-04-27','18:50:00','20:55:00',27000);
/*!40000 ALTER TABLE `event_days` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `Event_ID` int NOT NULL AUTO_INCREMENT,
  `Venue_ID` int NOT NULL,
  `Category_ID` int NOT NULL,
  `Title` varchar(100) NOT NULL,
  `Description` text NOT NULL,
  `Start_date` datetime NOT NULL,
  `End_date` datetime NOT NULL,
  `Price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `Capacity` int NOT NULL DEFAULT '0',
  `Image_URL` varchar(2048) DEFAULT 'default_event.jpg',
  `Accessibility_Flag` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`Event_ID`),
  KEY `Venue_ID` (`Venue_ID`),
  KEY `Category_ID` (`Category_ID`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`Venue_ID`) REFERENCES `venues` (`Venue_ID`) ON DELETE CASCADE,
  CONSTRAINT `events_ibfk_2` FOREIGN KEY (`Category_ID`) REFERENCES `categories` (`Category_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,1,1,'Rock Night Live','A night of classic rock.','2026-04-23 22:50:00','2026-05-02 23:59:00',20.00,2000,'default_event.jpg',1),(3,4,3,'Bristol City vs Cardiff','Championship Match.','2026-04-27 18:50:00','2026-04-27 20:55:00',30.00,27000,'city-vs-cardiff.jpg',1),(4,3,4,'Modern Art Expo','Exhibition of local artists.','2025-06-12 10:00:00','2025-06-15 18:00:00',10.00,500,'modern-art.jpg',1),(5,7,6,'Summer Rave','Electronic music all night.','2025-07-01 22:00:00','2025-07-02 04:00:00',20.00,1500,'rave.jpg',0),(6,6,2,'The Crucible','Dramatic play.','2025-07-05 19:30:00','2025-07-05 22:30:00',18.00,550,'the-crucible.jpg',1),(7,5,1,'Indie Band Showcase','Up and coming bands.','2026-04-18 04:00:00','2026-04-19 08:00:00',12.00,350,'default_event.jpg',0),(8,8,5,'Space Discovery','Interactive science show.','2026-04-17 03:10:00','2026-04-18 13:00:00',8.00,500,'default_event.jpg',0),(10,10,6,'DnB Allstars','Drum and Bass night.','2026-07-25 21:00:00','2026-07-26 03:00:00',22.00,800,'drum-bass.jpg',0),(11,10,1,'Summer Solstice Festival','Enjoy the summer vibes with amazing music.','2026-06-20 10:00:00','2026-06-20 22:00:00',50.00,500,'summer-solstice.jpg',0),(13,8,5,'Tech Innovators Conference','Meet the innovators behind today\'s tech.','2026-06-06 13:00:00','2026-06-06 17:30:00',50.00,100,'alexandre-pellaes-6vAjp0pscX0-unsplash.jpg',1),(15,9,7,'May Food & Wine Tasting','Taste the new culinary delights.','2026-05-22 15:30:00','2026-05-22 20:00:00',50.00,50,'food-tasting.jpg',1),(17,3,5,'Ancient Relics Museum Tour','Join us on a journey to view the wonderful relics of the past times.','2026-05-02 13:30:00','2026-05-02 17:00:00',15.00,20,'prehistoric.jpg',1),(18,8,5,'Science Showcase','Experience the Galaxy','2026-05-13 08:30:00','2026-05-13 13:30:00',5.00,10,'galaxy.jpg',1);
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `Ticket_ID` int NOT NULL AUTO_INCREMENT,
  `Booking_ID` int NOT NULL,
  `Code` varchar(50) NOT NULL,
  `Ticket_Status` enum('Valid','Active','Expired','Cancelled') DEFAULT 'Valid',
  `Activated_Time` datetime DEFAULT NULL,
  PRIMARY KEY (`Ticket_ID`),
  UNIQUE KEY `Code` (`Code`),
  KEY `Booking_ID` (`Booking_ID`),
  CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`Booking_ID`) REFERENCES `bookings` (`Booking_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tickets`
--

LOCK TABLES `tickets` WRITE;
/*!40000 ALTER TABLE `tickets` DISABLE KEYS */;
INSERT INTO `tickets` VALUES (1,1,'ROC-ZD63-44CB','Cancelled',NULL),(2,2,'ROC-X41U-1CF4','Valid','2026-04-23 22:43:40'),(4,4,'ANC-0B61-78DB','Valid',NULL),(5,4,'ANC-VVZ6-78DB','Valid',NULL),(6,4,'ANC-OAMP-78DB','Valid',NULL),(7,4,'ANC-001C-78DB','Valid',NULL),(8,4,'ANC-GNNY-78DB','Valid',NULL),(9,4,'ANC-9SLR-78DB','Valid',NULL),(10,4,'ANC-FTXV-78DB','Valid',NULL),(11,4,'ANC-BG22-78DB','Valid',NULL),(12,4,'ANC-ZWAV-78DB','Valid',NULL),(13,4,'ANC-719U-78DB','Valid',NULL),(14,5,'ANC-W3GD-82C9','Cancelled',NULL),(15,5,'ANC-HNC0-82C9','Cancelled',NULL),(16,5,'ANC-JB7G-82C9','Cancelled',NULL),(17,5,'ANC-D8IN-82C9','Cancelled',NULL),(18,5,'ANC-EXQ1-82C9','Cancelled',NULL),(19,5,'ANC-ON0D-82C9','Cancelled',NULL),(20,5,'ANC-FADG-82C9','Cancelled',NULL),(21,5,'ANC-O85V-82C9','Cancelled',NULL),(22,5,'ANC-G2WY-82C9','Cancelled',NULL),(23,5,'ANC-WBTX-82C9','Cancelled',NULL),(24,6,'SCI-ZVQW-2940','Cancelled',NULL),(25,6,'SCI-XCHA-2940','Cancelled',NULL),(26,6,'SCI-IVG7-2940','Cancelled',NULL),(27,6,'SCI-81PC-2940','Cancelled',NULL),(28,6,'SCI-FSF9-2940','Cancelled',NULL),(29,6,'SCI-YWCE-2940','Cancelled',NULL),(30,6,'SCI-UCIK-2940','Cancelled',NULL),(31,7,'SCI-K7QN-A5CD','Cancelled',NULL),(32,7,'SCI-ZY2J-A5CD','Cancelled',NULL),(33,7,'SCI-LRNZ-A5CD','Cancelled',NULL),(34,8,'BRI-IKKE-7412','Cancelled',NULL),(37,10,'ROC-YGKK-10AE','Valid','2026-04-24 18:44:31'),(38,11,'BRI-1HTV-E79E','Valid','2026-04-24 18:50:06'),(39,12,'MAY-Q15Y-F2FA','Cancelled',NULL),(40,13,'BRI-IKZU-849C','Valid',NULL),(41,14,'ROC-K200-36B2','Valid',NULL),(42,15,'ROC-S5GY-6AFF','Valid','2026-04-24 20:54:49');
/*!40000 ALTER TABLE `tickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `Transaction_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Booking_ID` int DEFAULT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `Payment_method` enum('Wallet','Google Pay','Apple Pay','Refund','PayPal') NOT NULL,
  `Transaction_Date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Transaction_ID`),
  KEY `User_ID` (`User_ID`),
  KEY `Booking_ID` (`Booking_ID`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`),
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`Booking_ID`) REFERENCES `bookings` (`Booking_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (1,2,1,0.00,'Apple Pay','2026-04-23 22:41:50'),(2,2,1,0.00,'Refund','2026-04-23 22:43:18'),(3,2,2,0.00,'Apple Pay','2026-04-23 22:43:28'),(5,1,NULL,200.00,'Wallet','2026-04-24 15:56:04'),(6,1,4,-150.00,'Wallet','2026-04-24 15:56:21'),(7,1,NULL,300.00,'Wallet','2026-04-24 15:56:37'),(8,1,5,-150.00,'Wallet','2026-04-24 15:57:38'),(9,2,NULL,200.00,'Wallet','2026-04-24 15:58:06'),(10,1,6,0.00,'PayPal','2026-04-24 16:28:29'),(11,1,7,0.00,'Apple Pay','2026-04-24 16:28:43'),(12,1,7,12.75,'Refund','2026-04-24 16:29:59'),(13,1,8,-27.00,'Wallet','2026-04-24 17:39:46'),(14,2,10,-18.00,'Wallet','2026-04-24 18:44:24'),(15,2,11,-30.00,'Wallet','2026-04-24 18:49:58'),(16,2,12,0.00,'Apple Pay','2026-04-24 19:55:04'),(17,1,8,0.00,'Refund','2026-04-24 20:27:53'),(18,1,13,-27.00,'Wallet','2026-04-24 20:28:08'),(19,1,NULL,10.00,'Wallet','2026-04-24 20:29:15'),(20,1,6,0.00,'Refund','2026-04-24 20:32:06'),(21,1,14,-18.00,'Wallet','2026-04-24 20:45:54'),(22,2,15,-18.00,'Wallet','2026-04-24 20:54:27'),(23,1,6,28.50,'Refund','2026-04-24 21:18:57'),(24,1,5,150.00,'Refund','2026-04-24 21:23:18'),(25,2,12,27.00,'Refund','2026-04-24 22:43:52');
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `user_ticket_info`
--

DROP TABLE IF EXISTS `user_ticket_info`;
/*!50001 DROP VIEW IF EXISTS `user_ticket_info`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `user_ticket_info` AS SELECT 
 1 AS `User_ID`,
 1 AS `Username`,
 1 AS `Title`,
 1 AS `Venue`,
 1 AS `Tickets_Purchased`,
 1 AS `Total_Price`,
 1 AS `Start_date`,
 1 AS `End_date`,
 1 AS `Code`,
 1 AS `Live_Status`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `User_ID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(100) NOT NULL,
  `First_name` varchar(100) DEFAULT NULL,
  `Last_name` varchar(100) DEFAULT NULL,
  `Email` varchar(150) NOT NULL,
  `Password_hash` varchar(255) NOT NULL,
  `Phone_number` varchar(15) DEFAULT NULL,
  `Avatar_URL` varchar(2048) DEFAULT NULL,
  `Role` enum('user','admin') DEFAULT 'user',
  `Terms_agreed` tinyint(1) NOT NULL DEFAULT '0',
  `Join_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`User_ID`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'alice_w','Alice','Wonder','alice@example.com','scrypt:32768:8:1$1xneyRLZQsJkPH5M$f20711edd5e2e5c574823e727db8666277fa5972888b03958750e0b6f322e0e76c317fb1f12da92a5268351741454c2a0f1900c65d3b20897518fbdfe130e51b','+447700900001',NULL,'user',1,'2025-01-01 10:00:00'),(2,'bob_builder','Bob','Builder','bob@example.com','scrypt:32768:8:1$PEbsvzSYOzQ1xaYV$cb62a215a8dcf33d8dfe36a247a96def3c674b2486cba95f40be661f01075074971c2d7ce170dae6d067e1e3ae46f51f4cfea04dde50e7352b3de9bacd49c7d5','+447700900002','Waves-1.png','admin',1,'2025-01-02 11:30:00'),(3,'charlie_c','Charlie','Chaplin','charlie@example.com','scrypt:32768:8:1$6zH5Dqj4P8LvMTxT$03d13c6e1c0d7bdaa53776ca9851760f08beaba0d20451ead3358d7a7cf35d50aa716b0069899ef4d4b2340d90da0dac67de4be0ac87eccad2e92f72ffe0d1d5','+447700900003',NULL,'user',1,'2025-01-03 14:15:00'),(4,'diana_p','Diana','Prince','diana@example.com','scrypt:32768:8:1$Q8VpK4Qt28LwtXvK$0b44ed77ffe5aa6825166d198c442a6390b62073a0c1b90d62cd3bfe96c621d9b8b327d9431ec79c83d3ddd5dbf8141d4f0421bc268dd1f60ab070167b5d51c6','+447700900004',NULL,'user',1,'2025-01-05 09:00:00'),(5,'evan_m','Evan','McGregor','evan@example.com','scrypt:32768:8:1$HuEKC0UOnNmpbzVY$20878a5e3f4ab9965b871011ee211bd90dcd484e993cc3794d32ea8a1f101593190589fd3dc3c91f5a3f5ac8acc17bf9098b75ee81e0e22e6a5ef68ccf265893','+447700900005',NULL,'user',1,'2025-01-10 16:45:00'),(6,'fiona_g','Fiona','Gallagher','fiona@example.com','scrypt:32768:8:1$Ep4LRWzSsAWFAjRO$183ccb2739ac570c047d69a33fec60cfc742a9eeadb4e548d6906946abf00023d8e4ea34d7872911ee648958ebe16e7b0181ef936216f85365138a17c9692d4e','+447700900006',NULL,'user',1,'2025-01-12 12:00:00'),(7,'george_l','George','Lucas','george@example.com','scrypt:32768:8:1$yLractRZ0whysSc3$a85490bd6bd2f397e1062fe96b186f2d5378db022f9dd691271358d1b8778c6a20358b367587f24fd4b1af598778d784f7be044f2b53e8a2366d60f206da4317','+447700900007',NULL,'user',1,'2025-01-15 08:30:00'),(8,'hannah_m','Hannah','Montana','hannah@example.com','scrypt:32768:8:1$eeeO3Lmznte9oark$1ea61de711a8048d6049bc12ba98c1102033cce894d7f04fff66b1ee25dfad105c069a54b947ef6d674cf82ac2bf16d2fc38a91ee11e30a304caa45d1b8d48e4','+447700900008',NULL,'user',1,'2025-01-20 18:20:00'),(13,'will_poulter','Will','Poulter','will@example.com','scrypt:32768:8:1$xajAszw37LYIWXff$c6ae324167e65934a527febf1e09d1487527a3bed1f9ffdd3d8e8c912183cf7005df8eed6d3aa3e4b7d4367f88844af95699333fa78eec738216e258d586cc8d','','Waves-1.png','user',1,'2026-04-24 20:14:31');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venues`
--

DROP TABLE IF EXISTS `venues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venues` (
  `Venue_ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Location` varchar(100) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `Description` text NOT NULL,
  `Type` varchar(50) NOT NULL,
  `Image_URL` varchar(2048) NOT NULL DEFAULT 'default.venue.jpg',
  `Max_Capacity` int NOT NULL DEFAULT '100',
  PRIMARY KEY (`Venue_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venues`
--

LOCK TABLES `venues` WRITE;
/*!40000 ALTER TABLE `venues` DISABLE KEYS */;
INSERT INTO `venues` VALUES (1,'Bristol O2 Academy','City Centre','Frogmore St, Bristol','Iconic music venue.','Concert Hall','o2.jpg',2000),(3,'Bristol Museum','Clifton','Queens Rd, Bristol','Historical museum venue.','Museum','bristol-musuem.jpg',500),(4,'Ashton Gate Stadium','Ashton','Ashton Rd, Bristol','Home of Bristol City FC.','Stadium','ashton-gate.png',27000),(5,'The Fleece','Redcliffe','12 St Thomas St, Bristol','Live music bar.','Live Music','fleece.png',400),(6,'Bristol Old Vic','City Centre','King St, Bristol','Oldest continuously working theatre.','Theatre','bristol-oldvic.jpg',550),(7,'Motion','Avon St','74-78 Avon St, Bristol','Large warehouse club.','Club','motion.png',1500),(8,'We The Curious','Harbourside','1 Millennium Sq, Bristol','Science centre.','Exhibition','we-the-curious.png',600),(9,'SS Great Britain','Harbourside','Great Western Dockyard','Historic ship venue.','Attraction','ss.jpg',250),(10,'Lakota','St Pauls','6 Upper York St, Bristol','Nightclub and events space.','Club','lakota.webp',800),(11,'Arnolfini','City Centre','16 Narrow Quay, Bristol','Renowned centre for contemporary arts and theatre','Theatre','Arnolfini.jpg',200);
/*!40000 ALTER TABLE `venues` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `waiting_list`
--

DROP TABLE IF EXISTS `waiting_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waiting_list` (
  `Waiting_List_ID` int NOT NULL AUTO_INCREMENT,
  `Event_ID` int NOT NULL,
  `User_ID` int NOT NULL,
  `Request_Date` datetime DEFAULT CURRENT_TIMESTAMP,
  `Status` enum('Waiting','Notified','Expired','Converted') DEFAULT 'Waiting',
  PRIMARY KEY (`Waiting_List_ID`),
  KEY `Event_ID` (`Event_ID`),
  KEY `User_ID` (`User_ID`),
  CONSTRAINT `waiting_list_ibfk_1` FOREIGN KEY (`Event_ID`) REFERENCES `events` (`Event_ID`) ON DELETE CASCADE,
  CONSTRAINT `waiting_list_ibfk_2` FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `waiting_list`
--

LOCK TABLES `waiting_list` WRITE;
/*!40000 ALTER TABLE `waiting_list` DISABLE KEYS */;
INSERT INTO `waiting_list` VALUES (2,18,2,'2026-04-24 16:29:12','Waiting'),(3,17,2,'2026-04-24 21:22:53','Waiting');
/*!40000 ALTER TABLE `waiting_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `wallet_balance`
--

DROP TABLE IF EXISTS `wallet_balance`;
/*!50001 DROP VIEW IF EXISTS `wallet_balance`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `wallet_balance` AS SELECT 
 1 AS `User_ID`,
 1 AS `Username`,
 1 AS `Balance`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `available_slots`
--

/*!50001 DROP VIEW IF EXISTS `available_slots`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `available_slots` AS select `e`.`Event_ID` AS `Event_ID`,`e`.`Title` AS `Title`,coalesce(sum(`ed`.`Day_Capacity`),0) AS `Total_Capacity`,count(`bd`.`Day_ID`) AS `Slots_Sold`,(coalesce(sum(`ed`.`Day_Capacity`),0) - count(`bd`.`Day_ID`)) AS `Slots_Left`,(case when ((coalesce(sum(`ed`.`Day_Capacity`),0) - count(`bd`.`Day_ID`)) <= 0) then 1 else 0 end) AS `If_Sold_Out` from (((`events` `e` left join `event_days` `ed` on((`e`.`Event_ID` = `ed`.`Event_ID`))) left join `bookings` `b` on(((`e`.`Event_ID` = `b`.`Event_ID`) and (`b`.`Booking_Status` = 'Success')))) left join `booking_days` `bd` on(((`b`.`Booking_ID` = `bd`.`Booking_ID`) and (`bd`.`Day_ID` = `ed`.`Day_ID`)))) group by `e`.`Event_ID` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `event_cards`
--

/*!50001 DROP VIEW IF EXISTS `event_cards`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `event_cards` AS select `e`.`Event_ID` AS `event_id`,`e`.`Title` AS `title`,`e`.`Description` AS `desc`,date_format(`e`.`Start_date`,'%Y-%m-%d') AS `date`,date_format(`e`.`End_date`,'%Y-%m-%d') AS `end_date`,`v`.`Name` AS `venue`,`c`.`Category_name` AS `category`,`e`.`Price` AS `price`,`e`.`Image_URL` AS `image`,`e`.`Capacity` AS `capacity`,(`e`.`Capacity` - coalesce((select count(0) from (`tickets` `t` join `bookings` `b` on((`t`.`Booking_ID` = `b`.`Booking_ID`))) where (`b`.`Event_ID` = `e`.`Event_ID`)),0)) AS `available_slots` from ((`events` `e` join `venues` `v` on((`e`.`Venue_ID` = `v`.`Venue_ID`))) join `categories` `c` on((`e`.`Category_ID` = `c`.`Category_ID`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `user_ticket_info`
--

/*!50001 DROP VIEW IF EXISTS `user_ticket_info`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `user_ticket_info` AS select `u`.`User_ID` AS `User_ID`,`u`.`Username` AS `Username`,`e`.`Title` AS `Title`,`v`.`Name` AS `Venue`,`b`.`Tickets_Purchased` AS `Tickets_Purchased`,(`b`.`Tickets_Purchased` * `b`.`Ticket_Price`) AS `Total_Price`,`e`.`Start_date` AS `Start_date`,`e`.`End_date` AS `End_date`,`t`.`Code` AS `Code`,(case when (`t`.`Ticket_Status` = 'Cancelled') then 'Cancelled' when (timestampdiff(SECOND,`e`.`End_date`,now()) >= 1) then 'Expired' when (timestampdiff(MINUTE,`t`.`Activated_Time`,now()) >= 10) then 'Used' when (`t`.`Activated_Time` is not null) then 'Active' when (`t`.`Activated_Time` is null) then 'Valid' else 'Valid' end) AS `Live_Status` from ((((`bookings` `b` join `users` `u` on((`b`.`User_ID` = `u`.`User_ID`))) join `events` `e` on((`b`.`Event_ID` = `e`.`Event_ID`))) join `venues` `v` on((`e`.`Venue_ID` = `v`.`Venue_ID`))) join `tickets` `t` on((`b`.`Booking_ID` = `t`.`Booking_ID`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `wallet_balance`
--

/*!50001 DROP VIEW IF EXISTS `wallet_balance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `wallet_balance` AS select `u`.`User_ID` AS `User_ID`,`u`.`Username` AS `Username`,coalesce(sum(`t`.`Amount`),0.00) AS `Balance` from (`users` `u` left join `transactions` `t` on((`u`.`User_ID` = `t`.`User_ID`))) group by `u`.`User_ID` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-25  0:38:40
