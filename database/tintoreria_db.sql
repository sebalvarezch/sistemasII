-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-04-2021 a las 14:27:18
-- Versión del servidor: 10.4.11-MariaDB
-- Versión de PHP: 7.4.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tintoreria_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `firstName` varchar(125) NOT NULL,
  `lastName` varchar(125) NOT NULL,
  `email` varchar(125) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `password` varchar(125) NOT NULL,
  `type` varchar(125) NOT NULL,
  `confirmCode` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `admin`
--

INSERT INTO `admin` (`id`, `firstName`, `lastName`, `email`, `mobile`, `address`, `password`, `type`, `confirmCode`) VALUES
(1, 'admin', '', 'admin', '04125555555', '', '$5$rounds=535000$tPXUzsOhDlvqhONE$xrck.vbTuMeNAaRlHKNnSYWrtilCMdkV39XleciCNU2', 'admin', 0),
(2, 'Adan', 'Torrealba', 'adan_e_torrealba@hotmail.com', '04144823887', 'Valencia', '$5$rounds=535000$BrqGxnfAHzEmpG4M$SzoD3BNfSVYYHrgSMSKg0/kYevAoH2ByjF0qlIeegx/', 'admin', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `uid` int(11) DEFAULT NULL,
  `ofname` text NOT NULL,
  `pid` int(11) NOT NULL,
  `quality` int(11) NOT NULL,
  `oplace` text NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `dstatus` varchar(10) NOT NULL,
  `odate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ddate` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `pName` varchar(125) NOT NULL,
  `price` int(11) NOT NULL,
  `description` text NOT NULL,
  `available` int(11) NOT NULL,
  `category` varchar(125) NOT NULL,
  `item` varchar(125) NOT NULL,
  `pCode` varchar(125) NOT NULL,
  `picture` text NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `products`
--

INSERT INTO `products` (`id`, `pName`, `price`, `description`, `available`, `category`, `item`, `pCode`, `picture`, `date`) VALUES
(1, 'Lavado de camisas de hombre', 2, 'Lavado de camisas de vestir para hombre', 10, 'camisa', 'camisa', 'c-l01', '14122873.jpg', '2021-03-29 15:59:34'),
(2, 'Planchado de camisas de hombre', 1, 'Planchado de camisas manga larga para hombres', 10, 'camisa', 'camisa', 'c-p01', '1a30bafc0af4e1000c49f63170645926.jpg', '2021-03-29 21:02:35'),
(3, 'Lavado de chemise para hombre', 2, 'Lavado de chemise para hombre', 10, 'chemise', 'chemise', 'ch-l01', 'amazon-dia-del-padre-chemise-polo.jpg', '2021-03-31 02:54:27'),
(4, 'Lavado y planchado de trajes para hombres', 15, 'Lavado y planchado de trajes completos (chalecos, camisa, pantalon, etc) para hombres', 10, 'traje', 'traje', 't-c01', '51oi88gYNuL._AC_UX385_.jpg', '2021-03-29 21:16:37'),
(5, 'Confeccion de sacos de hombre', 5, 'corte y confección de sacos y camisas de hombre', 10, 'traje', 'traje', 't-cc01', 'escoger-un-traje-01.jpg', '2021-03-29 21:18:10'),
(6, 'confeccion de camisas para hombre', 3, 'Corte y conrfeccion para camisas para hombre', 10, 'camisa', 'camisa', 'c-cc01', 'D_NQ_NP_856379-MLV32164360275_092019-W.jpg', '2021-03-29 21:19:26'),
(7, 'Planchado de chemises para hombre', 1, 'Planchado de chemises para hombre', 10, 'chemise', 'chemise', 'ch-p01', '53c21e0929fb47d3b778772a590a594c--polo-shirts-for-men-cotton-polo-shirts.jpg', '2021-03-29 21:20:32'),
(8, 'Confeccion de corbatas', 1, 'Corte y confeccion de corbatas para hombre', 10, 'corbata', 'corbata', 'co-cc01', 'corbata-saten-pala-estrecha.jpg', '2021-03-29 21:22:38'),
(9, 'Lavado de franelas para hombre', 2, 'Lavado de franelas para hombre', 10, 'franela', 'franela', 'f-l01', 'image_1024.jpg', '2021-03-29 21:24:01'),
(10, 'Planchado de franelas de hombre', 1, 'Planchado de franelas de hombre', 10, 'franela', 'franela', 'f-p01', 'Franela-blanca-1.png', '2021-03-29 21:24:53'),
(11, 'Confeccion de pantalones de hombre', 4, 'Corte y confección de pantalones de vestir para hombres', 10, 'pantalon', 'pantalon', 'p-cc01', '3918736a2625a98f1215b2b32831f853.jpg', '2021-03-29 21:26:58'),
(12, 'Lavado de jeans de hombre', 4, 'Lavado de pantalones jeans para hombre', 10, 'jean', 'jean', 'j-l01', 'pantalon-escalada-trekking-garbi-azul-hombre.jpg', '2021-03-29 21:28:13'),
(13, 'Confeccion de pantalones jeans para hombres', 4, 'Corte y confeccion de pantalones jeans para hombre', 10, 'jean', 'jean', 'j-cc01', 'pantalon-jeans-furor-maverick-corte-vaquero.jpg', '2021-03-29 21:32:07'),
(14, 'Lavado de sueter para hombre', 3, 'Lavado de sueteres para hombre', 10, 'sueter', 'sueter', 's-l01', 'sueter-lacoste-ah3467-21-9m0-masculino.jpg', '2021-03-29 21:33:29'),
(15, 'Confeccion de sueteres de hombre', 4, 'Corte y confeccion de sueteres para hombre', 10, 'sueter', 'sueter', 's-cc01', 'sueter-tommy-hilfiger-c8878d1793-921-masculino.jpg', '2021-03-29 21:34:27'),
(16, 'Lavado de camisas de mujer', 2, 'Lavado de camisas manga larga de mujer', 10, 'camisa', 'camisa', 'c-l02', 'camisa-sarga-manga-larga-mujer.jpg', '2021-03-31 02:40:40'),
(17, 'Planchado de camisas de mujer', 1, 'Planchado de camisas manga larga de mujer', 10, 'camisa', 'camisa', 'c-p02', 'camisa-mujer-manga-larga-strech-velilla.jpg', '2021-03-31 02:42:21'),
(18, 'Lavado de chemise para mujer', 2, 'Lavado de chemise para mujer', 10, 'chemise', 'chemise', 'ch-l02', 'D_NQ_NP_749436-MLV32160378337_092019-O.jpg', '2021-03-31 02:51:12'),
(19, 'Planchado de chemises para mujer', 1, 'Planchado de chemises para mujer', 10, 'chemise', 'chemise', 'ch-p02', 'Chemise-naranja-mujer.png', '2021-03-31 02:55:37'),
(20, 'Lavado de corbatas', 0, 'Lavado de corbatas por unidad', 10, 'corbata', 'corbata', 'co-l01', 'rop_0066.jpg', '2021-03-31 02:58:57'),
(21, 'Planchado de corbatas', 0, 'Planchado de corbata por unidad', 10, 'corbata', 'corbata', 'c-p01', 'Una-corbata-de-Georgia-Stripe.jpeg', '2021-03-31 02:59:40'),
(22, 'Lavado de pantalon de hombre', 2, 'Lavado de pantalon de vestir para hombre', 10, 'pantalon', 'pantalon', 'p-l01', 'unnamed.jpg', '2021-03-31 03:02:32'),
(23, 'Lavado de pantalon de mujer', 2, 'Lavado de pantalon de vestir para mujer', 10, 'pantalon', 'pantalon', 'p-l02', '31b22fedfd892691c20cb963cc6e3628.jpg', '2021-03-31 03:03:50'),
(24, 'Planchado de pantalon de mujer', 2, 'Planchado de pantalon de vestir para mujer', 10, 'pantalon', 'pantalon', 'p-p01', '0dbfcbcdebb028df80dec754b96b1e26.jpg', '2021-03-31 03:04:37'),
(25, 'Confeccion de pantalones de mujer', 4, 'Corte y confeccion de pantalones de vestir para mujeres', 10, 'pantalon', 'pantalon', 'p-cc02', 'pantalon-recto-vestir-mujer-azul-marino.jpg', '2021-03-31 03:05:41'),
(26, 'Lavado de saco de mujer', 5, 'Lavado de saco de vestir para mujer', 10, 'traje', 'traje', 't-l01', '329749313ffe475fa276bc1a78237a62.jpeg', '2021-03-31 03:07:49'),
(27, 'Confeccion de trajes de mujeres', 13, 'Corte y confeccion de trajes para mujeres', 10, 'traje', 'traje', 't-cc02', 'HTB1REKYPXXXXXcJXFXX760XFXXXj.png', '2021-03-31 03:08:46'),
(28, 'Lavado y planchado de trajes para mujeres', 15, 'Lavado, secado y planchado de traje de vestir para mujeres', 10, 'traje', 'traje', 't-c02', 'traje-mujer.jpg', '2021-03-31 03:09:38');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `product_level`
--

CREATE TABLE `product_level` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `lavado` varchar(3) NOT NULL,
  `planchado` varchar(3) NOT NULL,
  `confeccion` varchar(3) NOT NULL,
  `completo` varchar(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `product_level`
--

INSERT INTO `product_level` (`id`, `product_id`, `lavado`, `planchado`, `confeccion`, `completo`) VALUES
(1, 1, 'yes', '', '', ''),
(2, 2, '', 'yes', '', ''),
(3, 3, 'yes', '', '', ''),
(4, 4, '', '', '', 'yes'),
(5, 5, '', '', 'yes', ''),
(6, 6, '', '', 'yes', ''),
(7, 7, '', 'yes', '', ''),
(8, 8, '', '', 'yes', ''),
(9, 9, 'yes', '', '', ''),
(10, 10, '', 'yes', '', ''),
(11, 11, '', '', 'yes', ''),
(12, 12, 'yes', '', '', ''),
(13, 13, '', '', 'yes', ''),
(14, 14, 'yes', '', '', ''),
(15, 15, '', '', 'yes', ''),
(16, 16, 'yes', '', '', ''),
(17, 17, '', 'yes', '', ''),
(18, 18, 'yes', '', '', ''),
(19, 19, '', 'yes', '', ''),
(20, 20, 'yes', '', '', ''),
(21, 21, '', 'yes', '', ''),
(22, 22, 'yes', '', '', ''),
(23, 23, 'yes', '', '', ''),
(24, 24, '', 'yes', '', ''),
(25, 25, '', '', 'yes', ''),
(26, 26, 'yes', '', '', ''),
(27, 27, '', '', 'yes', ''),
(28, 28, '', '', '', 'yes');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `product_view`
--

CREATE TABLE `product_view` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(100) NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(125) NOT NULL,
  `email` varchar(125) NOT NULL,
  `username` varchar(125) NOT NULL,
  `password` varchar(125) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `reg_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `online` varchar(1) NOT NULL,
  `activation` varchar(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `product_level`
--
ALTER TABLE `product_level`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `product_view`
--
ALTER TABLE `product_view`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT de la tabla `product_level`
--
ALTER TABLE `product_level`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT de la tabla `product_view`
--
ALTER TABLE `product_view`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
