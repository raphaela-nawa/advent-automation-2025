import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export default function DeepZoom({ activeItem, onClose }) {
    // If no active item, we could show an intro or nothing.
    // GAC style: Active item usually takes over or sits prominently.
    // We'll make it an overlay or a top section. 
    // Given MVP, let's make it a top section Hero that expands when something is active.

    return (
        <AnimatePresence mode="wait">
            {activeItem && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="w-full bg-gac-dark text-gac-light p-6 md:p-12 flex flex-col items-center justify-center min-h-[50vh] relative overflow-hidden"
                >
                    {/* Background blur effect */}
                    <div
                        className="absolute inset-0 opacity-20 bg-cover bg-center blur-3xl scale-110"
                        style={{ backgroundImage: `url(${activeItem.image})` }}
                    />

                    <div className="relative z-10 w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
                        <div className="order-2 md:order-1 space-y-4">
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                <span className="inline-block px-3 py-1 bg-gac-accent/20 text-gac-accent text-xs font-bold tracking-wider uppercase rounded-full mb-2">
                                    Now Narrating
                                </span>
                                <h1 className="text-3xl md:text-5xl font-light leading-tight">
                                    {activeItem.title}
                                </h1>
                                <p className="text-lg text-white/60 mt-2 font-light">
                                    {activeItem.creator}, {activeItem.year}
                                </p>
                                <p className="text-white/80 mt-6 leading-relaxed max-w-prose">
                                    {activeItem.description}
                                </p>
                            </motion.div>
                        </div>

                        <motion.div
                            className="order-1 md:order-2 flex justify-center"
                            layoutId={`artwork-${activeItem.id}`}
                        >
                            <img
                                src={activeItem.image}
                                alt={activeItem.title}
                                className="max-h-[50vh] w-auto object-contain rounded-lg shadow-2xl"
                            />
                        </motion.div>
                    </div>
                </motion.div>
            )}
            {!activeItem && (
                <div className="h-[50vh] flex items-center justify-center bg-gac-light text-gac-dark p-8">
                    <div className="text-center max-w-xl">
                        <h1 className="text-4xl md:text-6xl font-light mb-4 text-gac-dark">
                            Museum <span className="text-gac-accent">Sync</span>
                        </h1>
                        <p className="text-lg text-gray-600">
                            Start the audio tour to explore the collection.
                            <br />
                            As the narration flows, the artwork will reveal itself.
                        </p>
                    </div>
                </div>
            )}
        </AnimatePresence>
    );
}
