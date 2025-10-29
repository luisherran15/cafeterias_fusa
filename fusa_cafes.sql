-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 29-10-2025 a las 01:20:11
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `fusa_cafes`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cafeterias`
--

CREATE TABLE `cafeterias` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `latitud` decimal(10,8) NOT NULL,
  `longitud` decimal(11,8) NOT NULL,
  `descripcion` text DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cafeterias`
--

INSERT INTO `cafeterias` (`id`, `admin_id`, `nombre`, `direccion`, `latitud`, `longitud`, `descripcion`) VALUES
(1, 2, 'cafeteria la carcel', 'cra 8va', 4.34405400, -74.36323200, ''),
(3, 2, 'cafe el kiosco', 'kiosco U', 4.33497000, -74.36988700, '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `certificados`
--

CREATE TABLE `certificados` (
  `id` int(11) NOT NULL,
  `cliente_id` int(11) NOT NULL,
  `fecha_emision` timestamp NOT NULL DEFAULT current_timestamp(),
  `codigo_certificado` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `certificados`
--

INSERT INTO `certificados` (`id`, `cliente_id`, `fecha_emision`, `codigo_certificado`) VALUES
(1, 3, '2025-10-27 20:25:37', '4A5736EB-70EE-48');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `descuentos_bonos`
--

CREATE TABLE `descuentos_bonos` (
  `id` int(11) NOT NULL,
  `cafeteria_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `porcentaje` int(11) NOT NULL,
  `fecha_expiracion` date NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `menus`
--

CREATE TABLE `menus` (
  `id` int(11) NOT NULL,
  `cafeteria_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text NOT NULL,
  `precio` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `menus`
--

INSERT INTO `menus` (`id`, `cafeteria_id`, `nombre`, `descripcion`, `precio`) VALUES
(2, 1, 'cafe sencillo', 'a', 5000.00),
(3, 3, 'cafe sencillo', 'cafe', 1000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `rol` enum('developer','admin','cliente') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `email`, `password`, `nombre`, `rol`) VALUES
(1, 'lfherran@Ucundinamarca.edu.co', 'scrypt:32768:8:1$t4njC2yNLgZOMqy8$b33e7135ed977698659405313e5ba5c5544a000f72c96dd5b34bb20bd7d7c891067ce316022622a95ef6e71f7fe7f6d3eb6cffe04ce3705763f97a14a4518f00', 'luis felipe herran', 'developer'),
(2, 'Hagodoy@Ucundinamarca.edu.co', 'scrypt:32768:8:1$BZrpcqAoT6PvKOAw$4e16d1763bd01338697512698fd993faf59fb78926ca9f949e8072627f89d58cd945b3a0f85d52e44a555d3fb0bd61bf2042b2da3d1266f085cd175429c2133c', 'hector godoy', 'admin'),
(3, 'luis@a.com', 'scrypt:32768:8:1$PSaEzak4Hq6thINO$028100de9c2bfcc09dfcf9b65b4a673df28e47043ff6d818aa5a998fe9d3fcde7fe5db83858a372971160339b7b91960c6806f2b9ef4c195fda2c369953f0ec9', 'felipe cliente', 'cliente'),
(4, 'cafe@Ucundinamarca.edu.co', 'scrypt:32768:8:1$lg3j3VGb8rkxm6pz$a1f79e660f01b166b6c44c396e44fe175a149f1d0744d01abbf1ff220e3c88ba1adc68224246f08b34b8e7273c69828b136db4e851ca1a9bc9c4d321eb2d72d6', 'cafe sencillo', 'cliente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `valoraciones`
--

CREATE TABLE `valoraciones` (
  `id` int(11) NOT NULL,
  `cliente_id` int(11) NOT NULL,
  `cafeteria_id` int(11) NOT NULL,
  `puntuacion` int(11) NOT NULL,
  `comentario` text NOT NULL,
  `fecha` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `visitas`
--

CREATE TABLE `visitas` (
  `id` int(11) NOT NULL,
  `cliente_id` int(11) NOT NULL,
  `cafeteria_id` int(11) NOT NULL,
  `fecha_visita` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `visitas`
--

INSERT INTO `visitas` (`id`, `cliente_id`, `cafeteria_id`, `fecha_visita`) VALUES
(1, 3, 1, '2025-10-27 15:25:30'),
(2, 4, 1, '2025-10-27 15:39:18');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cafeterias`
--
ALTER TABLE `cafeterias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id` (`id`),
  ADD KEY `fk_cafeterias_admin` (`admin_id`);

--
-- Indices de la tabla `certificados`
--
ALTER TABLE `certificados`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo_certificado` (`codigo_certificado`),
  ADD KEY `idx_cliente_certificado` (`cliente_id`),
  ADD KEY `idx_codigo_certificado` (`codigo_certificado`);

--
-- Indices de la tabla `descuentos_bonos`
--
ALTER TABLE `descuentos_bonos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cafeteria_id` (`cafeteria_id`);

--
-- Indices de la tabla `menus`
--
ALTER TABLE `menus`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cafeteria_id` (`cafeteria_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indices de la tabla `valoraciones`
--
ALTER TABLE `valoraciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cliente_id` (`cliente_id`),
  ADD KEY `cafeteria_id` (`cafeteria_id`);

--
-- Indices de la tabla `visitas`
--
ALTER TABLE `visitas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cliente_id` (`cliente_id`),
  ADD KEY `cafeteria_id` (`cafeteria_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cafeterias`
--
ALTER TABLE `cafeterias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `certificados`
--
ALTER TABLE `certificados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `descuentos_bonos`
--
ALTER TABLE `descuentos_bonos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `menus`
--
ALTER TABLE `menus`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `valoraciones`
--
ALTER TABLE `valoraciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `visitas`
--
ALTER TABLE `visitas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cafeterias`
--
ALTER TABLE `cafeterias`
  ADD CONSTRAINT `fk_cafeterias_admin` FOREIGN KEY (`admin_id`) REFERENCES `usuarios` (`id`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `certificados`
--
ALTER TABLE `certificados`
  ADD CONSTRAINT `certificados_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `descuentos_bonos`
--
ALTER TABLE `descuentos_bonos`
  ADD CONSTRAINT `fk_descuentos_cafeteria` FOREIGN KEY (`cafeteria_id`) REFERENCES `cafeterias` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `menus`
--
ALTER TABLE `menus`
  ADD CONSTRAINT `fk_menus_cafeteria` FOREIGN KEY (`cafeteria_id`) REFERENCES `cafeterias` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `valoraciones`
--
ALTER TABLE `valoraciones`
  ADD CONSTRAINT `fk_valoraciones_cafeteria` FOREIGN KEY (`cafeteria_id`) REFERENCES `cafeterias` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_valoraciones_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `usuarios` (`id`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `visitas`
--
ALTER TABLE `visitas`
  ADD CONSTRAINT `fk_visitas_cafeteria` FOREIGN KEY (`cafeteria_id`) REFERENCES `cafeterias` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_visitas_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
