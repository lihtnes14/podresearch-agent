import unittest
from backend.utils.chunking import chunk_transcript, format_timestamp


class TestChunking(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(5), "00:05")
        self.assertEqual(format_timestamp(65), "01:05")
        self.assertEqual(format_timestamp(3599), "59:59")
        self.assertEqual(format_timestamp(3600), "60:00")
        self.assertEqual(format_timestamp(6300), "105:00")

    def test_chunk_transcript_standard(self):
        transcript = (
            "[00:10] Introduction to the topic.\n"
            "[02:30] Discussion of the first key point.\n"
            "[05:15] Moving on to the second topic in next chunk.\n"
            "[08:45] Concluding thoughts for chunk 2.\n"
        )
        chunks = chunk_transcript(transcript, chunk_duration=300)

        self.assertEqual(len(chunks), 2)
        # Chunk 1: 00:00 to 05:00 (first 300 seconds)
        self.assertEqual(chunks[0]["chunk_id"], 1)
        self.assertEqual(chunks[0]["start_timestamp"], "00:00")
        self.assertEqual(chunks[0]["end_timestamp"], "05:00")
        self.assertEqual(len(chunks[0]["segments"]), 2)
        self.assertEqual(chunks[0]["segments"][0]["text"], "Introduction to the topic.")

        # Chunk 2: 05:00 to 10:00 (300 to 600 seconds)
        self.assertEqual(chunks[1]["chunk_id"], 2)
        self.assertEqual(chunks[1]["start_timestamp"], "05:00")
        self.assertEqual(chunks[1]["end_timestamp"], "10:00")
        self.assertEqual(len(chunks[1]["segments"]), 2)

    def test_chunk_transcript_handles_over_99_minutes(self):
        # Transcripts over 99 minutes (e.g. 105 minutes) must not be dropped by regex
        transcript = (
            "[10:00] Early discussion.\n"
            "[105:30] Late discussion after 100 minutes.\n"
        )
        chunks = chunk_transcript(transcript, chunk_duration=300)
        self.assertTrue(len(chunks) >= 2)
        found_late = any(
            any("105:30" in seg["timestamp"] for seg in c["segments"])
            for c in chunks
        )
        self.assertTrue(found_late, "Segment at 105:30 was unexpectedly dropped")

    def test_chunk_transcript_empty_or_malformed(self):
        # Empty input
        self.assertEqual(chunk_transcript(""), [])

        # Lines without timestamps should be safely ignored without throwing error
        malformed = "Just some text without timestamp\nAnother line without brackets\n"
        self.assertEqual(chunk_transcript(malformed), [])


if __name__ == "__main__":
    unittest.main()

