import React from 'react';
import { motion } from 'framer-motion';

export default function ArtworkGallery({ items, activeItemId, onItemClick }) {
    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4 pb-24">
            {items.map((item) => {
                const isActive = activeItemId === item.id;
                return (
                    <motion.div
                        key={item.id}
                        layoutId={`artwork-${item.id}`}
                        className={`relative group cursor-pointer aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 transition-colors ${isActive ? 'border-gac-accent' : 'border-transparent hover:border-gray-200'
                            }`}
                        onClick={() => onItemClick(item)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <img
                            src={item.image}
                            alt={item.title}
                            className="w-full h-full object-cover filter group-hover:brightness-110 transition-all"
                            loading="lazy"
                        />
                        {isActive && (
                            <div className="absolute inset-0 bg-gac-accent/10 flex items-center justify-center">
                                <span className="sr-only">Now Playing</span>
                            </div>
                        )}
                        <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent">
                            <p className="text-white text-sm font-medium truncate">{item.title}</p>
                            <p className="text-white/70 text-xs truncate">{item.creator}</p>
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
}
