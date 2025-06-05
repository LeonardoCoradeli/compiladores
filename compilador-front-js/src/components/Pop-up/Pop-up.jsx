import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X as IconX } from "lucide-react";
import "./Pop-up.css";

const popupVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 },
};

const errorIconVariants = {
  pulse: {
    scale: [1, 1.2, 1],
    transition: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
  },
};

export default function Popup({ isOpen, onClose, children }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="popup-backdrop"
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={popupVariants}
        >
          <motion.div
            className="popup-content"
            initial="hidden"
            animate="visible"
            exit="exit"
            variants={popupVariants}
            transition={{ duration: 0.25 }}
          >
            <button className="popup-close" onClick={onClose} aria-label="Fechar">
              <IconX size={20} />
            </button>

            <motion.div
              className="popup-error-icon"
              variants={errorIconVariants}
              animate="pulse"
            >
              <IconX size={96} color="#e74c3c" />
            </motion.div>

            <div className="popup-message">{children}</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
