import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define paths
const csvPath = path.resolve(__dirname, '../../day05/data/processed/matched_items_with_examples.csv');
const jsonOutputPath = path.resolve(__dirname, '../src/data/temporal-metadata.json');

console.log(`Reading CSV from: ${csvPath}`);

try {
    const csvFile = fs.readFileSync(csvPath, 'utf8');

    Papa.parse(csvFile, {
        header: true,
        complete: (results) => {
            const data = results.data;
            console.log(`Found ${data.length} rows.`);

            const metadata = data
                .filter(row => row.item_mention && row.timestamp && row.tainacan_title)
                .map((row, index) => {
                    // Convert HH:MM:SS to seconds
                    const [hours, minutes, seconds] = row.timestamp.split(':').map(Number);
                    const startTime = hours * 3600 + minutes * 60 + seconds;

                    // Estimate duration (placeholder logic: 30 seconds per item if not specified)
                    // Ideally we'd look at the next item's timestamp
                    const duration = 30;
                    const endTime = startTime + duration;

                    return {
                        id: row.tainacan_item_id || `item-${index}`,
                        start: startTime,
                        end: endTime,
                        title: row.tainacan_title,
                        description: row.context, // Using context as description
                        // Placeholder visuals for now
                        image: `https://via.placeholder.com/600x400?text=${encodeURIComponent(row.tainacan_title)}`,
                        creator: row.author_name || 'Unknown',
                        year: row.creation_date || 'Unknown'
                    };
                })
                .sort((a, b) => a.start - b.start);

            // Adjust end times to match start of next item to avoid overlaps/gaps if desired
            for (let i = 0; i < metadata.length - 1; i++) {
                if (metadata[i].end > metadata[i + 1].start) {
                    metadata[i].end = metadata[i + 1].start;
                }
            }

            console.log(`Processed ${metadata.length} valid items.`);

            fs.writeFileSync(jsonOutputPath, JSON.stringify(metadata, null, 2));
            console.log(`Written JSON to: ${jsonOutputPath}`);
        },
        error: (err) => {
            console.error("Papa parse error:", err);
        }
    });

} catch (err) {
    console.error("Error reading file:", err);
}
