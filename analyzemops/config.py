__all__ = ["Config"]

class Config(object):
    
    site_midnight = 0.166
    detection_file_columns = {"diaId": "det_id", 
                              "visitId": "field_id", 
                              "objectId": "object_name", 
                              "ra": "ra_deg", 
                              "dec": "dec_deg", 
                              "mjd": "epoch_mjd", 
                              "mag": "mag", 
                              "snr": "mag_sigma"}
    detection_file_read_params = {"sep": ","}
    detection_file_special_ids = {"FD": -1, 
                                  "NS": -2}
    
    
    detection_table = "Detections"
    diasources_table = "DiaSources"
    mapping_table = "Mapping"
    object_table = "AllObjects"
    tracklet_table = "AllTracklets"
    tracklet_members_table = "TrackletMembers"
    track_table = "AllTracks"
    track_members_table = "TrackMembers"
    verbose = True