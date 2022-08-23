from ArtistsUpdate import artists_update
from TracksUpdate import tracks_update
from AlbumsUpdate import albums_update

print("here")

if __name__ == "__main__":
    #artists_update()
    #tracks_update()
    albums_update()

    '''
    artists_names = get_distinct_values_column("artist_name")

    print(len(artists_names))
    print(artists_names[:10])

    artists_data = [(artist_data[0], get_artist_id(artist_data[0])) for artist_data in tqdm(artists_names)]
    print(artists_data[:3])

    print(len(artists_data))
    print(type(artists_data))

    insert_artist(artists_data)
    delete_duplicate("artists")
    get_data_table("artists", "artist_name")
    '''
    '''
    tracks_names = get_distinct_values_column("track_name, artist_name")
    print(len(tracks_names))
    print(tracks_names[:10])

    # for track_artist_name in tqdm(tracks_names[:100]):
        # print(track_artist_name)

    print(get_track_id(tracks_names[0][0], tracks_names[0][1]))
    tracks_ids = {(track_artist_name[0], track_artist_name[1]): get_track_id(track_artist_name[0], track_artist_name[1])
                  for track_artist_name in tqdm(tracks_names)}  # [:100]
    print({k: tracks_ids[k] for k in list(tracks_ids)[:10]})
    print(len(tracks_ids))
    tracks_ids = {key: value for key, value in tracks_ids.items()  if value != ""}
    print(len(tracks_ids))

    ids_duplicated = get_duplicated_ids(tracks_ids)
    print(ids_duplicated)
    print(len(ids_duplicated))

    num_parts_list = (len(tracks_ids) - 1) // 50
    print(range(num_parts_list))

    for num in range(0):
        print(num)

    if len(tracks_ids) > 50:
        tracks_data = []
        for num_it in tqdm(range(num_parts_list+1)):
            lower_bound = num_it*50
            upper_bound = min(len(tracks_ids), (num_it+1)*50)
            tracks_data = tracks_data + get_tracks_data_from_id(list(tracks_ids.values())[lower_bound:upper_bound])
    else:
        tracks_data = get_tracks_data_from_id(tracks_ids)

    print(tracks_data[:10])
    print(len(tracks_data))

    insert_track(tracks_data)
    get_data_table("tracks", "track_id")
    delete_duplicate("tracks")
    get_data_table("tracks", "track_id")
    '''
