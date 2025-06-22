'use client'
import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import Image from "next/image";
import "./style.scss";
import { Cover } from "@/components/ui/cover";

const Hero = () => {
    const containerRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"],
    });

    const rotate = useTransform(scrollYProgress, [0, 1], [15, 0]);
    const scale = useTransform(scrollYProgress, [0.5, 1], [0.9, 1]);
    const translate = useTransform(scrollYProgress, [0, 1], [0, -100]);

    return (
        <div ref={containerRef} className="hero-container">
            <div className="hero-content">
                <Header translate={translate} />
                <Card rotate={rotate} scale={scale} />
            </div>
        </div>
    );
};

const Header = ({ translate }) => {
    return (
        <motion.div
            style={{ translateY: translate }}
            className="hero-header"
        >
            <h1 className="text-4xl md:text-4xl lg:text-6xl font-semibold max-w-7xl mx-auto text-center mt-6 relative z-20 py-6 bg-clip-text text-transparent bg-gradient-to-b from-neutral-200 via-white to-white">
                 DevCommerce <br /> лучшие <Cover>dev-ресурсы</Cover>
            </h1>
        </motion.div>
    );
};

const Card = ({ rotate, scale }) => {
    return (
        <motion.div
            style={{
                rotateX: rotate,
                scale,
                boxShadow:
                    "0 0 #0000004d, 0 9px 20px #0000004a, 0 37px 37px #00000042, 0 84px 50px #00000026, 0 149px 60px #0000000a, 0 233px 65px #00000003",
            }}
            className="hero-card"
        >
            <div
                className="hero-card-content"
            >
                <Image src={'/hero-image.png'} layout="fill" objectFit="cover" alt="hero image" />
            </div>
        </motion.div>
    );
};

export default Hero;