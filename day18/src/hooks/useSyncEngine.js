import { useMemo } from 'react';
import metadata from '../data/temporal-metadata.json';

export function useSyncEngine(currentTime) {
    const activeItem = useMemo(() => {
        return metadata.find(item => currentTime >= item.start && currentTime < item.end);
    }, [currentTime]);

    return activeItem || null;
}
