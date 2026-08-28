// clients/unity/Assets/Scripts/JsonWire.cs
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEngine;

namespace CivilizationClone.UnityClient
{
    internal static class JsonWire
    {
        public static string Object(params (string Key, object Value)[] fields)
        {
            var builder = new StringBuilder("{");
            for (var index = 0; index < fields.Length; index++)
            {
                if (index > 0) builder.Append(',');
                builder.Append(Quote(fields[index].Key)).Append(':').Append(Value(fields[index].Value));
            }
            return builder.Append('}').ToString();
        }

        public static string Dictionary(IDictionary<string, object> fields)
        {
            var builder = new StringBuilder("{");
            var first = true;
            foreach (var pair in fields)
            {
                if (!first) builder.Append(',');
                first = false;
                builder.Append(Quote(pair.Key)).Append(':').Append(Value(pair.Value));
            }
            return builder.Append('}').ToString();
        }

        public static T Parse<T>(string json) where T : class => JsonUtility.FromJson<T>(json);

        public static T[] ParseArray<T>(string json)
        {
            var wrapper = JsonUtility.FromJson<ArrayWrapper<T>>("{\"items\":" + json + "}");
            return wrapper?.items ?? Array.Empty<T>();
        }

        public static string Quote(string text)
        {
            if (text == null) return "null";
            var builder = new StringBuilder("\"");
            foreach (var c in text)
            {
                switch (c)
                {
                    case '\\': builder.Append("\\\\"); break;
                    case '"': builder.Append("\\\""); break;
                    case '\n': builder.Append("\\n"); break;
                    case '\r': builder.Append("\\r"); break;
                    case '\t': builder.Append("\\t"); break;
                    default:
                        if (c < 0x20) builder.Append("\\u").Append(((int)c).ToString("x4"));
                        else builder.Append(c);
                        break;
                }
            }
            return builder.Append('"').ToString();
        }

        private static string Value(object value)
        {
            return value switch
            {
                null => "null",
                string text => Quote(text),
                bool boolean => boolean ? "true" : "false",
                byte or sbyte or short or ushort or int or uint or long or ulong => Convert.ToString(value, CultureInfo.InvariantCulture),
                float or double or decimal => Convert.ToString(value, CultureInfo.InvariantCulture),
                IDictionary<string, object> dictionary => Dictionary(dictionary),
                _ => throw new ArgumentException($"Unsupported JSON wire value: {value.GetType().FullName}")
            };
        }

        [Serializable] private sealed class ArrayWrapper<T> { public T[] items; }
    }
}
