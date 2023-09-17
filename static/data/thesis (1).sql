-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Εξυπηρετητής: 127.0.0.1
-- Χρόνος δημιουργίας: 08 Μάη 2023 στις 19:26:09
-- Έκδοση διακομιστή: 10.4.28-MariaDB
-- Έκδοση PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Βάση δεδομένων: `thesis`
--

-- --------------------------------------------------------

--
-- Δομή πίνακα για τον πίνακα `areas`
--

CREATE TABLE `areas` (
  `id` int(250) NOT NULL,
  `code` varchar(5) NOT NULL,
  `name` varchar(50) NOT NULL,
  `mmax_PAP` float NOT NULL,
  `mmax_MOUN` float NOT NULL,
  `mmax_EQ` float NOT NULL,
  `mmax` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Δομή πίνακα για τον πίνακα `coordinates`
--

CREATE TABLE `coordinates` (
  `area_code` varchar(10) NOT NULL,
  `latitude` float NOT NULL,
  `longitude` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Δομή πίνακα για τον πίνακα `events`
--

CREATE TABLE `events` (
  `time` timestamp(5) NOT NULL DEFAULT current_timestamp(5) ON UPDATE current_timestamp(5),
  `Mw` float NOT NULL,
  `longitude` float NOT NULL,
  `latitude` float NOT NULL,
  `depth` float NOT NULL,
  `id` varchar(50) NOT NULL,
  `strike` varchar(50) NOT NULL,
  `dip` varchar(100) NOT NULL,
  `rake` varchar(100) NOT NULL,
  `mtlist` varchar(250) NOT NULL,
  `of_area` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Ευρετήρια για άχρηστους πίνακες
--

--
-- Ευρετήρια για πίνακα `areas`
--
ALTER TABLE `areas`
  ADD PRIMARY KEY (`code`);

--
-- Ευρετήρια για πίνακα `coordinates`
--
ALTER TABLE `coordinates`
  ADD KEY `area_code` (`area_code`);

--
-- Περιορισμοί για άχρηστους πίνακες
--

--
-- Περιορισμοί για πίνακα `coordinates`
--
ALTER TABLE `coordinates`
  ADD CONSTRAINT `area_code` FOREIGN KEY (`area_code`) REFERENCES `areas` (`code`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
