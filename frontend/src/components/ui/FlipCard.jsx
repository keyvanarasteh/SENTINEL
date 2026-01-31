import { cn } from '../../lib/utils';
import { ArrowRight, Code2, Copy, Rocket, Zap, Check, RotateCw } from 'lucide-react';
import { useState } from 'react';

export default function FlipCard({
    title = 'Build MVPs Fast',
    subtitle = 'Launch your idea in record time',
    description = 'Copy, paste, customize—and launch your MVP faster than ever with our developer-first component library.',
    features = [],
    color = '#ff2e88', // Default color, can be overridden
    icon: Icon = Rocket
}) {
    const [isFlipped, setIsFlipped] = useState(false);

    return (
        <div
            style={{
                '--primary': color ?? '#2563eb',
            }}
            className="group relative h-[420px] w-full [perspective:2000px] cursor-pointer"
            onMouseEnter={() => setIsFlipped(true)}
            onMouseLeave={() => setIsFlipped(false)}
            onClick={() => setIsFlipped(!isFlipped)} // Touch support
        >
            <div
                className={cn(
                    'relative h-full w-full',
                    '[transform-style:preserve-3d]',
                    'transition-all duration-700 ease-out',
                    isFlipped
                        ? '[transform:rotateY(180deg)]'
                        : '[transform:rotateY(0deg)]',
                )}
            >
                {/* --- FRONT OF CARD --- */}
                <div
                    className={cn(
                        'absolute inset-0 h-full w-full',
                        '[transform:rotateY(0deg)] [backface-visibility:hidden]',
                        'overflow-hidden rounded-3xl',
                        'bg-[#0f111a]', // Deep dark background
                        'border border-white/10',
                        'shadow-2xl',
                        'flex flex-col items-center justify-center p-8 text-center',
                        'transition-all duration-700',
                        'group-hover:border-[var(--primary)]/50 group-hover:shadow-[0_0_50px_rgba(var(--primary),0.2)]',
                        isFlipped ? 'opacity-0' : 'opacity-100',
                    )}
                >
                    {/* Ambient Glow */}
                    <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-[var(--primary)]/10 via-transparent to-transparent opacity-60 group-hover:opacity-100 transition-opacity duration-500" />

                    {/* Animated Ring Background */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-20 group-hover:opacity-30 transition-opacity duration-500">
                        <div className="w-[300px] h-[300px] border border-[var(--primary)]/30 rounded-full animate-[spin_10s_linear_infinite]" />
                        <div className="absolute w-[200px] h-[200px] border border-[var(--primary)]/20 rounded-full animate-[spin_15s_linear_infinite_reverse]" />
                    </div>

                    {/* Icon Container */}
                    <div className="relative z-10 mb-8 p-4 rounded-2xl bg-white/5 border border-white/10 shadow-lg backdrop-blur-sm group-hover:scale-110 transition-transform duration-500">
                        <Icon className="h-10 w-10 text-[var(--primary)] drop-shadow-[0_0_10px_rgba(var(--primary),0.8)]" />
                    </div>

                    {/* Title (Question) - Making it BIG and CLEAR */}
                    <h3 className="relative z-10 text-2xl font-bold text-white leading-tight mb-3 drop-shadow-md">
                        {title}
                    </h3>

                    {/* Subtitle (Category) */}
                    <span className="relative z-10 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest text-[var(--primary)] bg-[var(--primary)]/10 border border-[var(--primary)]/20">
                        {subtitle}
                    </span>

                    {/* Flip Hint */}
                    <div className="absolute bottom-6 flex items-center gap-2 text-gray-500 text-xs font-medium uppercase tracking-wider opacity-60 group-hover:opacity-100 transition-opacity">
                        <RotateCw size={14} /> Flip to Reveal
                    </div>
                </div>

                {/* --- BACK OF CARD --- */}
                <div
                    className={cn(
                        'absolute inset-0 h-full w-full',
                        '[transform:rotateY(180deg)] [backface-visibility:hidden]',
                        'rounded-3xl p-8',
                        'bg-[#12141c]',
                        'border border-white/10',
                        'shadow-2xl',
                        'flex flex-col',
                        'transition-all duration-700',
                        'group-hover:border-[var(--primary)]/40',
                        !isFlipped ? 'opacity-0' : 'opacity-100',
                    )}
                >
                    {/* Header with Icon */}
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/10">
                        <div className="p-2 rounded-lg bg-[var(--primary)]/20">
                            <Zap className="h-5 w-5 text-[var(--primary)]" />
                        </div>
                        <span className="text-sm font-bold text-gray-400 uppercase tracking-wider">Answer</span>
                    </div>

                    {/* Answer Text - High Contrast for Readability */}
                    <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                        <p className="text-lg leading-relaxed text-gray-100 font-medium">
                            {description}
                        </p>

                        {/* Features List */}
                        {features && features.length > 0 && (
                            <div className="mt-6 flex flex-wrap gap-2">
                                {features.map((feature, index) => (
                                    <span
                                        key={index}
                                        className="px-2 py-1 bg-white/5 border border-white/5 rounded-md text-xs text-gray-300 flex items-center gap-1.5"
                                    >
                                        <Check size={10} className="text-[var(--primary)]" />
                                        {feature}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Footer Action */}
                    <div className="mt-6 pt-4 border-t border-white/10">
                        <button className="w-full py-3 rounded-xl bg-white/5 hover:bg-[var(--primary)]/20 hover:text-white text-gray-400 font-semibold text-sm transition-all duration-300 flex items-center justify-center gap-2 group/btn">
                            Learn More <ArrowRight size={16} className="group-hover/btn:translate-x-1 transition-transform" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
